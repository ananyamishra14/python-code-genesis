
import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Calendar, ChevronDown, ChevronUp, Download, FileText, RefreshCw, Search, TrendingUp } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

// Mock data types
interface CategorySales {
  category: string;
  sales: number;
  revenue: number;
}

interface ProductSales {
  id: number;
  name: string;
  sku: string;
  category: string;
  sales: number;
  revenue: number;
  avgPrice: number;
  profit: number;
  margin: number;
}

interface TimeSeriesData {
  date: string;
  sales: number;
  revenue: number;
}

interface TrendData {
  key: string;
  name: string;
  value: number;
  change: number;
  trend: 'up' | 'down' | 'neutral';
}

// Mock data fetching functions
const fetchCategorySales = async (): Promise<CategorySales[]> => {
  return [
    { category: "Electronics", sales: 1245, revenue: 65420 },
    { category: "Clothing", sales: 876, revenue: 32180 },
    { category: "Home & Kitchen", sales: 543, revenue: 27650 },
    { category: "Sports & Outdoors", sales: 432, revenue: 21560 },
    { category: "Beauty & Personal Care", sales: 321, revenue: 12840 }
  ];
};

const fetchTopProducts = async (): Promise<ProductSales[]> => {
  return [
    { 
      id: 1, 
      name: "Premium Wireless Headphones", 
      sku: "ELEC-101", 
      category: "Electronics", 
      sales: 245, 
      revenue: 24500, 
      avgPrice: 99.99, 
      profit: 12250, 
      margin: 0.50 
    },
    { 
      id: 2, 
      name: "Organic Cotton T-Shirt", 
      sku: "CLOTH-202", 
      category: "Clothing", 
      sales: 198, 
      revenue: 5940, 
      avgPrice: 29.99, 
      profit: 2970, 
      margin: 0.50 
    },
    { 
      id: 3, 
      name: "Smart Watch Series 7", 
      sku: "ELEC-305", 
      category: "Electronics", 
      sales: 156, 
      revenue: 31200, 
      avgPrice: 199.99, 
      profit: 15600, 
      margin: 0.50 
    },
    { 
      id: 4, 
      name: "Ergonomic Office Chair", 
      sku: "HOME-118", 
      category: "Home & Kitchen", 
      sales: 87, 
      revenue: 13050, 
      avgPrice: 149.99, 
      profit: 5220, 
      margin: 0.40 
    },
    { 
      id: 5, 
      name: "Yoga Mat Pro", 
      sku: "SPORT-423", 
      category: "Sports & Outdoors", 
      sales: 132, 
      revenue: 3960, 
      avgPrice: 29.99, 
      profit: 1980, 
      margin: 0.50 
    }
  ];
};

const fetchSalesTimeSeries = async (): Promise<TimeSeriesData[]> => {
  // Generate 30 days of data
  const data: TimeSeriesData[] = [];
  const today = new Date();
  
  for (let i = 30; i >= 0; i--) {
    const date = new Date();
    date.setDate(today.getDate() - i);
    
    // Generate some realistic data with weekend peaks
    const dayOfWeek = date.getDay();
    const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
    const baseSales = isWeekend ? 40 : 25;
    
    const sales = Math.floor(baseSales + Math.random() * 20);
    const avgPrice = 30 + Math.random() * 10;
    const revenue = Math.floor(sales * avgPrice);
    
    data.push({
      date: date.toISOString().split('T')[0],
      sales,
      revenue
    });
  }
  
  return data;
};

const fetchTrendData = async (): Promise<TrendData[]> => {
  return [
    {
      key: "total_sales",
      name: "Total Sales",
      value: 3417,
      change: 12.5,
      trend: "up"
    },
    {
      key: "total_revenue",
      name: "Total Revenue",
      value: 159650,
      change: 8.3,
      trend: "up"
    },
    {
      key: "avg_order_value",
      name: "Avg. Order Value",
      value: 46.72,
      change: -2.1,
      trend: "down"
    },
    {
      key: "profit_margin",
      name: "Profit Margin",
      value: 42.8,
      change: 0.5,
      trend: "up"
    }
  ];
};

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

const InventoryAnalytics: React.FC = () => {
  const [timeRange, setTimeRange] = useState<string>("30d");
  const [categoryFilter, setCategoryFilter] = useState<string>("all");
  
  // Fetch data using React Query
  const { data: categorySales, isLoading: categorySalesLoading } = useQuery({
    queryKey: ['categorySales', timeRange],
    queryFn: fetchCategorySales
  });
  
  const { data: topProducts, isLoading: topProductsLoading } = useQuery({
    queryKey: ['topProducts', timeRange, categoryFilter],
    queryFn: fetchTopProducts
  });
  
  const { data: salesTimeSeries, isLoading: timeSeriesLoading } = useQuery({
    queryKey: ['salesTimeSeries', timeRange],
    queryFn: fetchSalesTimeSeries
  });
  
  const { data: trendData, isLoading: trendDataLoading } = useQuery({
    queryKey: ['trendData', timeRange],
    queryFn: fetchTrendData
  });
  
  // Helper function to format currency
  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(value);
  };
  
  const formatNumber = (value: number): string => {
    return new Intl.NumberFormat('en-US').format(value);
  };
  
  const formatPercent = (value: number): string => {
    return `${value.toFixed(1)}%`;
  };

  return (
    <div className="container mx-auto py-6">
      <div className="flex flex-col gap-6">
        <h1 className="text-3xl font-bold">Inventory Analytics</h1>
        
        {/* Filters and Controls */}
        <div className="flex flex-col sm:flex-row justify-between gap-4">
          <div className="flex flex-wrap gap-2">
            <Select value={timeRange} onValueChange={setTimeRange}>
              <SelectTrigger className="w-[140px]">
                <Calendar className="mr-2 h-4 w-4" />
                <SelectValue placeholder="Time Range" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="7d">Last 7 days</SelectItem>
                <SelectItem value="30d">Last 30 days</SelectItem>
                <SelectItem value="90d">Last 90 days</SelectItem>
                <SelectItem value="1y">Last year</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={categoryFilter} onValueChange={setCategoryFilter}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Category" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Categories</SelectItem>
                <SelectItem value="electronics">Electronics</SelectItem>
                <SelectItem value="clothing">Clothing</SelectItem>
                <SelectItem value="home">Home & Kitchen</SelectItem>
                <SelectItem value="sports">Sports & Outdoors</SelectItem>
                <SelectItem value="beauty">Beauty & Personal Care</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <div className="flex gap-2">
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                type="search"
                placeholder="Search products..."
                className="w-[200px] pl-8"
              />
            </div>
            
            <Button variant="outline" size="icon">
              <RefreshCw className="h-4 w-4" />
            </Button>
            
            <Button variant="outline" size="icon">
              <Download className="h-4 w-4" />
            </Button>
          </div>
        </div>
        
        {/* Key Metrics */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {trendDataLoading ? (
            Array(4).fill(0).map((_, i) => (
              <Card key={i} className="animate-pulse">
                <CardHeader className="pb-2">
                  <div className="h-4 w-24 bg-muted rounded"></div>
                </CardHeader>
                <CardContent>
                  <div className="h-8 w-20 bg-muted rounded"></div>
                  <div className="h-4 w-16 bg-muted rounded mt-2"></div>
                </CardContent>
              </Card>
            ))
          ) : (
            trendData?.map((item) => (
              <Card key={item.key}>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    {item.name}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {item.key.includes('revenue') || item.key.includes('value')
                      ? formatCurrency(item.value)
                      : item.key.includes('margin')
                      ? formatPercent(item.value)
                      : formatNumber(item.value)}
                  </div>
                  <div className={`flex items-center text-sm ${
                    item.trend === 'up' ? 'text-green-600' : 
                    item.trend === 'down' ? 'text-red-600' : 
                    'text-muted-foreground'
                  }`}>
                    {item.trend === 'up' ? (
                      <ChevronUp className="mr-1 h-4 w-4" />
                    ) : item.trend === 'down' ? (
                      <ChevronDown className="mr-1 h-4 w-4" />
                    ) : (
                      <span className="mr-1">-</span>
                    )}
                    {Math.abs(item.change)}% from previous period
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
        
        {/* Charts and Tables */}
        <Tabs defaultValue="overview" className="w-full">
          <TabsList className="grid grid-cols-3 w-full md:w-[400px]">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="products">Products</TabsTrigger>
            <TabsTrigger value="categories">Categories</TabsTrigger>
          </TabsList>
          
          {/* Overview Tab */}
          <TabsContent value="overview">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              {/* Sales Trend Chart */}
              <Card>
                <CardHeader>
                  <CardTitle>Sales Trend</CardTitle>
                  <CardDescription>
                    Units sold over time with revenue overlay
                  </CardDescription>
                </CardHeader>
                <CardContent className="h-80">
                  {timeSeriesLoading ? (
                    <div className="h-full flex items-center justify-center">
                      <p>Loading chart data...</p>
                    </div>
                  ) : (
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart
                        data={salesTimeSeries}
                        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis 
                          dataKey="date" 
                          tick={{ fontSize: 12 }}
                          tickFormatter={(value) => {
                            const date = new Date(value);
                            return `${date.getMonth() + 1}/${date.getDate()}`;
                          }}
                        />
                        <YAxis yAxisId="left" orientation="left" stroke="#8884d8" />
                        <YAxis yAxisId="right" orientation="right" stroke="#82ca9d" />
                        <Tooltip 
                          formatter={(value, name) => {
                            if (name === 'revenue') {
                              return [formatCurrency(value as number), 'Revenue'];
                            }
                            return [value, 'Units Sold'];
                          }}
                          labelFormatter={(label) => {
                            const date = new Date(label);
                            return date.toLocaleDateString();
                          }}
                        />
                        <Legend />
                        <Line 
                          yAxisId="left"
                          type="monotone" 
                          dataKey="sales" 
                          stroke="#8884d8" 
                          activeDot={{ r: 8 }}
                          name="Units Sold"
                        />
                        <Line 
                          yAxisId="right"
                          type="monotone" 
                          dataKey="revenue" 
                          stroke="#82ca9d" 
                          name="Revenue"
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  )}
                </CardContent>
              </Card>
              
              {/* Category Distribution */}
              <Card>
                <CardHeader>
                  <CardTitle>Category Distribution</CardTitle>
                  <CardDescription>
                    Sales and revenue by product category
                  </CardDescription>
                </CardHeader>
                <CardContent className="h-80">
                  {categorySalesLoading ? (
                    <div className="h-full flex items-center justify-center">
                      <p>Loading chart data...</p>
                    </div>
                  ) : (
                    <div className="h-full grid grid-rows-2 gap-4">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={categorySales}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            outerRadius={70}
                            fill="#8884d8"
                            dataKey="sales"
                            nameKey="category"
                            label={({ category, percent }) => `${category}: ${(percent * 100).toFixed(0)}%`}
                          >
                            {categorySales?.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Pie>
                          <Tooltip 
                            formatter={(value) => [formatNumber(value as number), 'Units Sold']}
                            labelFormatter={(label) => label as string}
                          />
                          <Legend />
                        </PieChart>
                      </ResponsiveContainer>
                      
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart
                          data={categorySales}
                          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                        >
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="category" />
                          <YAxis tickFormatter={(value) => `$${value / 1000}k`} />
                          <Tooltip 
                            formatter={(value) => [formatCurrency(value as number), 'Revenue']}
                          />
                          <Bar dataKey="revenue" fill="#82ca9d" name="Revenue" />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
            
            {/* Recent Reports */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>Recent Reports</CardTitle>
                  <CardDescription>
                    Automatically generated inventory reports
                  </CardDescription>
                </div>
                <Button variant="outline" size="sm">
                  <FileText className="mr-2 h-4 w-4" />
                  View All
                </Button>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Card className="bg-muted/40">
                    <CardHeader className="p-4">
                      <CardTitle className="text-base">Weekly Sales Summary</CardTitle>
                    </CardHeader>
                    <CardContent className="p-4 pt-0">
                      <p className="text-sm text-muted-foreground">Generated on April 10, 2023</p>
                      <div className="mt-2 flex justify-between items-center">
                        <Button variant="outline" size="sm">
                          <Download className="mr-2 h-3 w-3" />
                          Download PDF
                        </Button>
                        <TrendingUp className="h-5 w-5 text-green-500" />
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card className="bg-muted/40">
                    <CardHeader className="p-4">
                      <CardTitle className="text-base">Inventory Status Report</CardTitle>
                    </CardHeader>
                    <CardContent className="p-4 pt-0">
                      <p className="text-sm text-muted-foreground">Generated on April 9, 2023</p>
                      <div className="mt-2 flex justify-between items-center">
                        <Button variant="outline" size="sm">
                          <Download className="mr-2 h-3 w-3" />
                          Download PDF
                        </Button>
                        <TrendingUp className="h-5 w-5 text-amber-500" />
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card className="bg-muted/40">
                    <CardHeader className="p-4">
                      <CardTitle className="text-base">Monthly Performance</CardTitle>
                    </CardHeader>
                    <CardContent className="p-4 pt-0">
                      <p className="text-sm text-muted-foreground">Generated on April 1, 2023</p>
                      <div className="mt-2 flex justify-between items-center">
                        <Button variant="outline" size="sm">
                          <Download className="mr-2 h-3 w-3" />
                          Download PDF
                        </Button>
                        <TrendingUp className="h-5 w-5 text-green-500" />
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          
          {/* Products Tab */}
          <TabsContent value="products">
            <Card>
              <CardHeader>
                <CardTitle>Top Selling Products</CardTitle>
                <CardDescription>
                  Products with the highest sales volume and revenue
                </CardDescription>
              </CardHeader>
              <CardContent>
                {topProductsLoading ? (
                  <div className="h-64 flex items-center justify-center">
                    <p>Loading product data...</p>
                  </div>
                ) : (
                  <div className="rounded-md border">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Product Name</TableHead>
                          <TableHead>SKU</TableHead>
                          <TableHead>Category</TableHead>
                          <TableHead className="text-right">Sales</TableHead>
                          <TableHead className="text-right">Revenue</TableHead>
                          <TableHead className="text-right">Avg. Price</TableHead>
                          <TableHead className="text-right">Profit</TableHead>
                          <TableHead className="text-right">Margin</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {topProducts?.map((product) => (
                          <TableRow key={product.id}>
                            <TableCell className="font-medium">{product.name}</TableCell>
                            <TableCell>{product.sku}</TableCell>
                            <TableCell>{product.category}</TableCell>
                            <TableCell className="text-right">{formatNumber(product.sales)}</TableCell>
                            <TableCell className="text-right">{formatCurrency(product.revenue)}</TableCell>
                            <TableCell className="text-right">{formatCurrency(product.avgPrice)}</TableCell>
                            <TableCell className="text-right">{formatCurrency(product.profit)}</TableCell>
                            <TableCell className="text-right">{formatPercent(product.margin * 100)}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                )}
                
                <div className="mt-6">
                  <h3 className="text-lg font-medium mb-4">Product Performance Comparison</h3>
                  {topProductsLoading ? (
                    <div className="h-64 flex items-center justify-center">
                      <p>Loading chart data...</p>
                    </div>
                  ) : (
                    <div className="h-64">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart
                          data={topProducts?.map(p => ({
                            name: p.name,
                            sales: p.sales,
                            revenue: p.revenue,
                            profit: p.profit
                          }))}
                          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                        >
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="name" />
                          <YAxis yAxisId="left" orientation="left" stroke="#8884d8" />
                          <YAxis yAxisId="right" orientation="right" stroke="#82ca9d" />
                          <Tooltip 
                            formatter={(value, name) => {
                              if (name === 'sales') {
                                return [formatNumber(value as number), 'Units Sold'];
                              }
                              return [formatCurrency(value as number), name as string];
                            }}
                          />
                          <Legend />
                          <Bar yAxisId="left" dataKey="sales" fill="#8884d8" name="Units Sold" />
                          <Bar yAxisId="right" dataKey="revenue" fill="#82ca9d" name="Revenue" />
                          <Bar yAxisId="right" dataKey="profit" fill="#ffc658" name="Profit" />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          
          {/* Categories Tab */}
          <TabsContent value="categories">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Category Performance</CardTitle>
                  <CardDescription>
                    Sales and revenue metrics by product category
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {categorySalesLoading ? (
                    <div className="h-64 flex items-center justify-center">
                      <p>Loading category data...</p>
                    </div>
                  ) : (
                    <div className="rounded-md border">
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Category</TableHead>
                            <TableHead className="text-right">Sales</TableHead>
                            <TableHead className="text-right">Revenue</TableHead>
                            <TableHead className="text-right">Avg. Per Unit</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {categorySales?.map((category) => (
                            <TableRow key={category.category}>
                              <TableCell className="font-medium">{category.category}</TableCell>
                              <TableCell className="text-right">{formatNumber(category.sales)}</TableCell>
                              <TableCell className="text-right">{formatCurrency(category.revenue)}</TableCell>
                              <TableCell className="text-right">
                                {formatCurrency(category.revenue / category.sales)}
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  )}
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader>
                  <CardTitle>Category Revenue Comparison</CardTitle>
                  <CardDescription>
                    Visual breakdown of revenue by category
                  </CardDescription>
                </CardHeader>
                <CardContent className="h-80">
                  {categorySalesLoading ? (
                    <div className="h-full flex items-center justify-center">
                      <p>Loading chart data...</p>
                    </div>
                  ) : (
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart
                        layout="vertical"
                        data={categorySales}
                        margin={{ top: 5, right: 30, left: 100, bottom: 5 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis type="number" tickFormatter={(value) => `$${value / 1000}k`} />
                        <YAxis type="category" dataKey="category" />
                        <Tooltip 
                          formatter={(value) => [formatCurrency(value as number), 'Revenue']}
                        />
                        <Legend />
                        <Bar dataKey="revenue" fill="#82ca9d" name="Revenue">
                          {categorySales?.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default InventoryAnalytics;
