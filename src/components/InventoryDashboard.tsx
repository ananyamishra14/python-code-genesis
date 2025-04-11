
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import { Badge } from "@/components/ui/badge";
import { useQuery } from '@tanstack/react-query';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Package, AlertTriangle, CheckCircle, TrendingUp, TrendingDown, ShoppingCart, Truck, Calendar } from 'lucide-react';

interface Product {
  id: number;
  name: string;
  sku: string;
  current_stock: number;
  reorder_point: number;
  optimal_stock: number | null;
  category: string;
  price: number;
  cost: number;
  stock_status: 'out_of_stock' | 'low_stock' | 'adequate' | 'overstocked';
}

interface InventoryAlert {
  product_id: number;
  product_name: string;
  alert_type: 'out_of_stock' | 'low_stock' | 'reorder' | 'overstocked';
  message: string;
  severity: 'critical' | 'warning' | 'info';
}

interface SalesData {
  date: string;
  revenue: number;
  units: number;
}

interface PredictionData {
  date: string;
  predicted_demand: number;
  confidence_lower: number;
  confidence_upper: number;
}

// Mock API functions - in a real app, these would be API calls
const fetchProducts = async (): Promise<Product[]> => {
  // Mock data for demonstration
  return [
    {
      id: 1,
      name: "Organic Cotton T-Shirt",
      sku: "TSHIRT-001",
      current_stock: 45,
      reorder_point: 20,
      optimal_stock: 60,
      category: "Clothing",
      price: 29.99,
      cost: 12.50,
      stock_status: "adequate"
    },
    {
      id: 2,
      name: "Wireless Headphones",
      sku: "AUDIO-156",
      current_stock: 8,
      reorder_point: 15,
      optimal_stock: 35,
      category: "Electronics",
      price: 89.99,
      cost: 42.75,
      stock_status: "low_stock"
    },
    {
      id: 3,
      name: "Standing Desk",
      sku: "FURN-238",
      current_stock: 0,
      reorder_point: 5,
      optimal_stock: 10,
      category: "Furniture",
      price: 349.99,
      cost: 175.50,
      stock_status: "out_of_stock"
    },
    {
      id: 4,
      name: "Stainless Water Bottle",
      sku: "BOTTLE-442",
      current_stock: 120,
      reorder_point: 50,
      optimal_stock: 80,
      category: "Accessories",
      price: 24.99,
      cost: 8.25,
      stock_status: "overstocked"
    },
    {
      id: 5,
      name: "Smart Watch",
      sku: "TECH-512",
      current_stock: 25,
      reorder_point: 10,
      optimal_stock: 30,
      category: "Electronics",
      price: 199.99,
      cost: 85.00,
      stock_status: "adequate"
    }
  ];
};

const fetchAlerts = async (): Promise<InventoryAlert[]> => {
  // Mock data for demonstration
  return [
    {
      product_id: 3,
      product_name: "Standing Desk",
      alert_type: "out_of_stock",
      message: "Item is out of stock. Reorder immediately.",
      severity: "critical"
    },
    {
      product_id: 2,
      product_name: "Wireless Headphones",
      alert_type: "low_stock",
      message: "Stock level below reorder point (8 < 15).",
      severity: "warning"
    },
    {
      product_id: 4,
      product_name: "Stainless Water Bottle",
      alert_type: "overstocked",
      message: "Current stock exceeds optimal level (120 > 80).",
      severity: "info"
    }
  ];
};

const fetchSalesData = async (): Promise<SalesData[]> => {
  // Mock data for demonstration
  return [
    { date: "2023-04-01", revenue: 2890, units: 54 },
    { date: "2023-04-02", revenue: 2350, units: 42 },
    { date: "2023-04-03", revenue: 3800, units: 67 },
    { date: "2023-04-04", revenue: 2950, units: 51 },
    { date: "2023-04-05", revenue: 3100, units: 58 },
    { date: "2023-04-06", revenue: 2700, units: 45 },
    { date: "2023-04-07", revenue: 4200, units: 73 },
    { date: "2023-04-08", revenue: 3900, units: 62 },
    { date: "2023-04-09", revenue: 3400, units: 59 },
    { date: "2023-04-10", revenue: 3200, units: 55 }
  ];
};

const fetchPredictions = async (): Promise<PredictionData[]> => {
  // Mock data for demonstration
  return [
    { date: "2023-04-11", predicted_demand: 58, confidence_lower: 45, confidence_upper: 71 },
    { date: "2023-04-12", predicted_demand: 62, confidence_lower: 48, confidence_upper: 76 },
    { date: "2023-04-13", predicted_demand: 57, confidence_lower: 44, confidence_upper: 70 },
    { date: "2023-04-14", predicted_demand: 65, confidence_lower: 50, confidence_upper: 80 },
    { date: "2023-04-15", predicted_demand: 70, confidence_lower: 54, confidence_upper: 86 },
    { date: "2023-04-16", predicted_demand: 59, confidence_lower: 46, confidence_upper: 72 },
    { date: "2023-04-17", predicted_demand: 63, confidence_lower: 49, confidence_upper: 77 }
  ];
};

// Helper function to render stock status badge
const StockStatusBadge = ({ status }: { status: Product['stock_status'] }) => {
  switch (status) {
    case 'out_of_stock':
      return <Badge variant="destructive">Out of Stock</Badge>;
    case 'low_stock':
      return <Badge variant="warning" className="bg-amber-500">Low Stock</Badge>;
    case 'adequate':
      return <Badge variant="outline" className="bg-green-100 text-green-800 border-green-300">Adequate</Badge>;
    case 'overstocked':
      return <Badge variant="secondary" className="bg-blue-100 text-blue-800 border-blue-300">Overstocked</Badge>;
    default:
      return null;
  }
};

// Helper function to render alert severity
const AlertSeverityIcon = ({ severity }: { severity: InventoryAlert['severity'] }) => {
  switch (severity) {
    case 'critical':
      return <AlertTriangle className="h-5 w-5 text-red-500" />;
    case 'warning':
      return <AlertTriangle className="h-5 w-5 text-amber-500" />;
    case 'info':
      return <CheckCircle className="h-5 w-5 text-blue-500" />;
    default:
      return null;
  }
};

const InventoryDashboard: React.FC = () => {
  const [selectedTab, setSelectedTab] = useState('overview');

  // Fetch products
  const { data: products, isLoading: productsLoading } = useQuery({
    queryKey: ['products'],
    queryFn: fetchProducts
  });

  // Fetch alerts
  const { data: alerts, isLoading: alertsLoading } = useQuery({
    queryKey: ['alerts'],
    queryFn: fetchAlerts
  });

  // Fetch sales data
  const { data: salesData, isLoading: salesLoading } = useQuery({
    queryKey: ['sales'],
    queryFn: fetchSalesData
  });

  // Fetch prediction data
  const { data: predictionData, isLoading: predictionsLoading } = useQuery({
    queryKey: ['predictions'],
    queryFn: fetchPredictions
  });

  // Calculate summary statistics
  const inventorySummary = React.useMemo(() => {
    if (!products) return null;
    
    const totalProducts = products.length;
    const totalUnits = products.reduce((sum, product) => sum + product.current_stock, 0);
    const totalValue = products.reduce((sum, product) => sum + (product.current_stock * product.price), 0);
    const lowStockCount = products.filter(p => p.stock_status === 'low_stock' || p.stock_status === 'out_of_stock').length;
    
    return {
      totalProducts,
      totalUnits,
      totalValue,
      lowStockCount
    };
  }, [products]);

  const chartConfig = {
    sales: {
      label: "Sales",
      theme: {
        light: "#0ea5e9",
        dark: "#38bdf8"
      }
    },
    prediction: {
      label: "Prediction",
      theme: {
        light: "#8b5cf6",
        dark: "#a78bfa"
      }
    },
    confidence: {
      label: "Confidence Interval",
      theme: {
        light: "#d8b4fe",
        dark: "#c4b5fd"
      }
    }
  };

  return (
    <div className="container mx-auto py-6">
      <div className="flex flex-col gap-6">
        <h1 className="text-3xl font-bold">Smart Inventory Dashboard</h1>
        
        <Tabs defaultValue="overview" value={selectedTab} onValueChange={setSelectedTab} className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="inventory">Inventory</TabsTrigger>
            <TabsTrigger value="predictions">Demand Predictions</TabsTrigger>
            <TabsTrigger value="alerts">Alerts</TabsTrigger>
          </TabsList>
          
          {/* Overview Tab */}
          <TabsContent value="overview">
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Inventory Value</CardTitle>
                  <Package className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    ${inventorySummary?.totalValue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00'}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Across {inventorySummary?.totalProducts || 0} products
                  </p>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Low Stock Items</CardTitle>
                  <AlertTriangle className="h-4 w-4 text-amber-500" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {inventorySummary?.lowStockCount || 0}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Products need reordering
                  </p>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Units</CardTitle>
                  <ShoppingCart className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {inventorySummary?.totalUnits.toLocaleString() || 0}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Items in stock
                  </p>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Predicted Demand</CardTitle>
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {!predictionsLoading && predictionData 
                      ? Math.round(predictionData.reduce((sum, day) => sum + day.predicted_demand, 0) / predictionData.length) 
                      : 0}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Units / day (next 7 days)
                  </p>
                </CardContent>
              </Card>
            </div>
            
            {/* Sales & Prediction Chart */}
            <Card className="mb-6">
              <CardHeader>
                <CardTitle>Sales & Demand Prediction</CardTitle>
                <CardDescription>
                  Historical sales with 7-day prediction
                </CardDescription>
              </CardHeader>
              <CardContent className="h-[300px]">
                {salesLoading || predictionsLoading ? (
                  <div className="h-full flex items-center justify-center">
                    <p>Loading chart data...</p>
                  </div>
                ) : (
                  <ChartContainer config={chartConfig} className="h-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart
                        data={[
                          ...(salesData || []).map(item => ({
                            date: new Date(item.date).toLocaleDateString(),
                            sales: item.units,
                          })),
                          ...(predictionData || []).map(item => ({
                            date: new Date(item.date).toLocaleDateString(),
                            prediction: item.predicted_demand,
                            confidenceLower: item.confidence_lower,
                            confidenceUpper: item.confidence_upper
                          }))
                        ]}
                        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <ChartTooltip content={<ChartTooltipContent />} />
                        <Legend />
                        <Line 
                          type="monotone" 
                          dataKey="sales" 
                          stroke="var(--color-sales)" 
                          strokeWidth={2} 
                          dot={{ r: 4 }} 
                          name="Historical Sales"
                        />
                        <Line 
                          type="monotone" 
                          dataKey="prediction" 
                          stroke="var(--color-prediction)" 
                          strokeWidth={2} 
                          strokeDasharray="5 5" 
                          dot={{ r: 4 }} 
                          name="Predicted Demand" 
                        />
                        <Line 
                          type="monotone" 
                          dataKey="confidenceLower" 
                          stroke="var(--color-confidence)" 
                          strokeWidth={1} 
                          strokeDasharray="3 3" 
                          dot={false} 
                          name="Confidence Lower" 
                        />
                        <Line 
                          type="monotone" 
                          dataKey="confidenceUpper" 
                          stroke="var(--color-confidence)" 
                          strokeWidth={1} 
                          strokeDasharray="3 3" 
                          dot={false} 
                          name="Confidence Upper" 
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </ChartContainer>
                )}
              </CardContent>
            </Card>
            
            {/* Recent Alerts */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Inventory Alerts</CardTitle>
                <CardDescription>
                  Items requiring attention
                </CardDescription>
              </CardHeader>
              <CardContent>
                {alertsLoading ? (
                  <p>Loading alerts...</p>
                ) : alerts && alerts.length > 0 ? (
                  <div className="space-y-4">
                    {alerts.map(alert => (
                      <div 
                        key={`${alert.product_id}-${alert.alert_type}`}
                        className="flex items-start gap-3 p-3 border rounded-lg bg-background"
                      >
                        <div className="mt-0.5">
                          <AlertSeverityIcon severity={alert.severity} />
                        </div>
                        <div>
                          <h4 className="font-medium">{alert.product_name}</h4>
                          <p className="text-sm text-muted-foreground">{alert.message}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p>No alerts to display.</p>
                )}
              </CardContent>
            </Card>
          </TabsContent>
          
          {/* Inventory Tab */}
          <TabsContent value="inventory">
            <Card>
              <CardHeader>
                <CardTitle>Current Inventory</CardTitle>
                <CardDescription>
                  Manage and monitor your stock levels
                </CardDescription>
              </CardHeader>
              <CardContent>
                {productsLoading ? (
                  <p>Loading inventory data...</p>
                ) : products && products.length > 0 ? (
                  <div className="rounded-md border">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Product Name</TableHead>
                          <TableHead>SKU</TableHead>
                          <TableHead>Category</TableHead>
                          <TableHead className="text-right">Current Stock</TableHead>
                          <TableHead className="text-right">Reorder Point</TableHead>
                          <TableHead className="text-right">Optimal Stock</TableHead>
                          <TableHead>Status</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {products.map(product => (
                          <TableRow key={product.id}>
                            <TableCell className="font-medium">{product.name}</TableCell>
                            <TableCell>{product.sku}</TableCell>
                            <TableCell>{product.category}</TableCell>
                            <TableCell className="text-right">{product.current_stock}</TableCell>
                            <TableCell className="text-right">{product.reorder_point}</TableCell>
                            <TableCell className="text-right">{product.optimal_stock || '-'}</TableCell>
                            <TableCell>
                              <StockStatusBadge status={product.stock_status} />
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                ) : (
                  <p>No inventory data available.</p>
                )}
              </CardContent>
            </Card>
            
            {/* Stock Value by Category */}
            <Card className="mt-6">
              <CardHeader>
                <CardTitle>Inventory Value by Category</CardTitle>
              </CardHeader>
              <CardContent className="h-[300px]">
                {productsLoading ? (
                  <div className="h-full flex items-center justify-center">
                    <p>Loading chart data...</p>
                  </div>
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={
                        products?.reduce((acc, product) => {
                          const existingCategory = acc.find(
                            item => item.category === product.category
                          );
                          
                          if (existingCategory) {
                            existingCategory.value += product.current_stock * product.price;
                          } else {
                            acc.push({
                              category: product.category,
                              value: product.current_stock * product.price
                            });
                          }
                          
                          return acc;
                        }, [] as Array<{ category: string; value: number }>)
                      }
                      margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="category" />
                      <YAxis 
                        tickFormatter={(value) => 
                          `$${value.toLocaleString(undefined, { 
                            minimumFractionDigits: 0, 
                            maximumFractionDigits: 0 
                          })}`
                        }
                      />
                      <Tooltip 
                        formatter={(value: number) => 
                          `$${value.toLocaleString(undefined, { 
                            minimumFractionDigits: 2, 
                            maximumFractionDigits: 2 
                          })}`
                        }
                      />
                      <Legend />
                      <Bar 
                        dataKey="value" 
                        name="Inventory Value" 
                        fill="#8884d8" 
                      />
                    </BarChart>
                  </ResponsiveContainer>
                )}
              </CardContent>
            </Card>
          </TabsContent>
          
          {/* Predictions Tab */}
          <TabsContent value="predictions">
            <Card className="mb-6">
              <CardHeader>
                <CardTitle>7-Day Demand Forecast</CardTitle>
                <CardDescription>
                  AI-powered prediction with confidence intervals
                </CardDescription>
              </CardHeader>
              <CardContent className="h-[300px]">
                {predictionsLoading ? (
                  <div className="h-full flex items-center justify-center">
                    <p>Loading prediction data...</p>
                  </div>
                ) : (
                  <ChartContainer config={chartConfig} className="h-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart
                        data={predictionData?.map(item => ({
                          date: new Date(item.date).toLocaleDateString(),
                          prediction: item.predicted_demand,
                          lower: item.confidence_lower,
                          upper: item.confidence_upper
                        }))}
                        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line 
                          type="monotone" 
                          dataKey="prediction" 
                          stroke="var(--color-prediction)" 
                          strokeWidth={2} 
                          name="Predicted Demand" 
                        />
                        <Line 
                          type="monotone" 
                          dataKey="lower" 
                          stroke="var(--color-confidence)" 
                          strokeWidth={1} 
                          strokeDasharray="3 3" 
                          name="Lower Bound" 
                        />
                        <Line 
                          type="monotone" 
                          dataKey="upper" 
                          stroke="var(--color-confidence)" 
                          strokeWidth={1} 
                          strokeDasharray="3 3" 
                          name="Upper Bound" 
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </ChartContainer>
                )}
              </CardContent>
            </Card>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Prediction Factors</CardTitle>
                  <CardDescription>
                    Key elements affecting demand predictions
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between border-b pb-2">
                      <div className="flex items-center">
                        <Calendar className="h-5 w-5 mr-2 text-blue-500" />
                        <span>Seasonal Patterns</span>
                      </div>
                      <span className="text-green-600">High Impact</span>
                    </div>
                    <div className="flex items-center justify-between border-b pb-2">
                      <div className="flex items-center">
                        <ShoppingCart className="h-5 w-5 mr-2 text-purple-500" />
                        <span>Recent Sales Trend</span>
                      </div>
                      <span className="text-green-600">High Impact</span>
                    </div>
                    <div className="flex items-center justify-between border-b pb-2">
                      <div className="flex items-center">
                        <TrendingUp className="h-5 w-5 mr-2 text-orange-500" />
                        <span>Promotional Activities</span>
                      </div>
                      <span className="text-amber-600">Medium Impact</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <Truck className="h-5 w-5 mr-2 text-gray-500" />
                        <span>Supply Chain Factors</span>
                      </div>
                      <span className="text-amber-600">Medium Impact</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader>
                  <CardTitle>Recommended Actions</CardTitle>
                  <CardDescription>
                    AI-suggested inventory management actions
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                      <h4 className="font-medium text-red-800 flex items-center">
                        <AlertTriangle className="h-4 w-4 mr-2" />
                        Urgent Restock Needed
                      </h4>
                      <p className="text-sm text-red-700 mt-1">
                        Order 10 units of Standing Desk (FURN-238) immediately to avoid lost sales.
                      </p>
                    </div>
                    
                    <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg">
                      <h4 className="font-medium text-amber-800 flex items-center">
                        <AlertTriangle className="h-4 w-4 mr-2" />
                        Reorder Soon
                      </h4>
                      <p className="text-sm text-amber-700 mt-1">
                        Place order for 25 units of Wireless Headphones (AUDIO-156) within 5 days.
                      </p>
                    </div>
                    
                    <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                      <h4 className="font-medium text-blue-800 flex items-center">
                        <TrendingDown className="h-4 w-4 mr-2" />
                        Reduce Inventory
                      </h4>
                      <p className="text-sm text-blue-700 mt-1">
                        Consider a promotion for Stainless Water Bottles to reduce excess inventory.
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
          
          {/* Alerts Tab */}
          <TabsContent value="alerts">
            <Card>
              <CardHeader>
                <CardTitle>Inventory Alerts</CardTitle>
                <CardDescription>
                  All active alerts requiring attention
                </CardDescription>
              </CardHeader>
              <CardContent>
                {alertsLoading ? (
                  <p>Loading alerts...</p>
                ) : alerts && alerts.length > 0 ? (
                  <div className="rounded-md border">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Severity</TableHead>
                          <TableHead>Product</TableHead>
                          <TableHead>Alert Type</TableHead>
                          <TableHead>Message</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {alerts.map(alert => (
                          <TableRow key={`${alert.product_id}-${alert.alert_type}`}>
                            <TableCell>
                              <div className="flex items-center">
                                <AlertSeverityIcon severity={alert.severity} />
                                <span className="ml-2 capitalize">{alert.severity}</span>
                              </div>
                            </TableCell>
                            <TableCell className="font-medium">{alert.product_name}</TableCell>
                            <TableCell className="capitalize">{alert.alert_type.replace(/_/g, ' ')}</TableCell>
                            <TableCell>{alert.message}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                ) : (
                  <p>No alerts to display.</p>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default InventoryDashboard;
