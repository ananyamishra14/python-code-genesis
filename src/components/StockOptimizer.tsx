
import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Slider } from "@/components/ui/slider";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { TabsContent } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useQuery } from '@tanstack/react-query';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Package, ArrowRight, TrendingUp, Calculator, RefreshCcw } from 'lucide-react';

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
  lead_time?: number;
}

interface OptimizationResult {
  product_id: number;
  current_stock: number;
  avg_daily_demand: number;
  demand_variability: number;
  safety_stock: number;
  reorder_point: number;
  economic_order_quantity: number;
  optimal_stock: number;
  service_level: number;
  lead_time: number;
  cost_analysis?: {
    current_policy: {
      holding_cost: number;
      stockout_probability: number;
      expected_stockouts: number;
      stockout_cost: number;
      total_cost: number;
    };
    optimal_policy: {
      holding_cost: number;
      stockout_probability: number;
      expected_stockouts: number;
      stockout_cost: number;
      total_cost: number;
    };
    potential_savings: number;
    savings_percent: number;
  };
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
      stock_status: "adequate",
      lead_time: 7
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
      stock_status: "low_stock",
      lead_time: 14
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
      stock_status: "out_of_stock",
      lead_time: 21
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
      stock_status: "overstocked",
      lead_time: 5
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
      stock_status: "adequate",
      lead_time: 10
    }
  ];
};

// Mock function for optimization
const optimizeStock = async (productId: number, serviceLevel: number, leadTime?: number): Promise<OptimizationResult> => {
  // In a real app, this would call your backend API
  return new Promise((resolve) => {
    // Wait a bit to simulate API call
    setTimeout(() => {
      const result: OptimizationResult = {
        product_id: productId,
        current_stock: 25,
        avg_daily_demand: 3.5,
        demand_variability: 1.2,
        safety_stock: 12,
        reorder_point: leadTime ? Math.round(3.5 * leadTime + 12) : 35,
        economic_order_quantity: 42,
        optimal_stock: leadTime ? Math.round(3.5 * leadTime + 12 + 42) : 77,
        service_level: serviceLevel,
        lead_time: leadTime || 10,
        cost_analysis: {
          current_policy: {
            holding_cost: 425.50,
            stockout_probability: 0.15,
            expected_stockouts: 3.2,
            stockout_cost: 368.75,
            total_cost: 794.25
          },
          optimal_policy: {
            holding_cost: 573.75,
            stockout_probability: 0.03,
            expected_stockouts: 0.5,
            stockout_cost: 57.50,
            total_cost: 631.25
          },
          potential_savings: 163.00,
          savings_percent: 20.5
        }
      };
      resolve(result);
    }, 1000);
  });
};

const StockOptimizer: React.FC = () => {
  const [selectedProductId, setSelectedProductId] = useState<number | null>(null);
  const [serviceLevel, setServiceLevel] = useState<number>(95);
  const [customLeadTime, setCustomLeadTime] = useState<number | null>(null);
  const [isOptimizing, setIsOptimizing] = useState<boolean>(false);
  const [optimizationResult, setOptimizationResult] = useState<OptimizationResult | null>(null);

  // Fetch products
  const { data: products, isLoading } = useQuery({
    queryKey: ['products'],
    queryFn: fetchProducts
  });

  // Find selected product
  const selectedProduct = products?.find(p => p.id === selectedProductId) || null;

  // Handle optimization
  const handleOptimize = async () => {
    if (!selectedProductId) return;
    
    setIsOptimizing(true);
    try {
      const result = await optimizeStock(
        selectedProductId, 
        serviceLevel / 100,
        customLeadTime || selectedProduct?.lead_time
      );
      setOptimizationResult(result);
    } catch (error) {
      console.error("Optimization failed:", error);
    } finally {
      setIsOptimizing(false);
    }
  };

  // Reset optimization
  const resetOptimization = () => {
    setOptimizationResult(null);
    setCustomLeadTime(null);
  };

  // Generate comparison data for charts
  const generateComparisonData = () => {
    if (!optimizationResult || !selectedProduct) return [];
    
    return [
      {
        name: "Current",
        reorderPoint: selectedProduct.reorder_point,
        optimalStock: selectedProduct.optimal_stock || 0,
        holdingCost: optimizationResult.cost_analysis?.current_policy.holding_cost || 0,
        stockoutCost: optimizationResult.cost_analysis?.current_policy.stockout_cost || 0,
      },
      {
        name: "Optimized",
        reorderPoint: optimizationResult.reorder_point,
        optimalStock: optimizationResult.optimal_stock,
        holdingCost: optimizationResult.cost_analysis?.optimal_policy.holding_cost || 0,
        stockoutCost: optimizationResult.cost_analysis?.optimal_policy.stockout_cost || 0,
      }
    ];
  };

  return (
    <div className="container mx-auto py-6">
      <div className="flex flex-col gap-6">
        <h1 className="text-3xl font-bold">Stock Level Optimizer</h1>
        
        <Card>
          <CardHeader>
            <CardTitle>Optimize Inventory Parameters</CardTitle>
            <CardDescription>
              Fine-tune your stock levels based on AI-powered demand predictions
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="product-select">Select Product</Label>
                  <Select
                    value={selectedProductId?.toString() || ""}
                    onValueChange={(value) => {
                      setSelectedProductId(Number(value));
                      resetOptimization();
                    }}
                  >
                    <SelectTrigger id="product-select">
                      <SelectValue placeholder="Select a product" />
                    </SelectTrigger>
                    <SelectContent>
                      {isLoading ? (
                        <SelectItem value="loading" disabled>Loading products...</SelectItem>
                      ) : products && products.length > 0 ? (
                        products.map(product => (
                          <SelectItem key={product.id} value={product.id.toString()}>
                            {product.name} ({product.sku})
                          </SelectItem>
                        ))
                      ) : (
                        <SelectItem value="none" disabled>No products available</SelectItem>
                      )}
                    </SelectContent>
                  </Select>
                </div>
                
                {selectedProduct && (
                  <>
                    <div className="space-y-2">
                      <Label htmlFor="service-level">
                        Service Level: {serviceLevel}%
                      </Label>
                      <Slider
                        id="service-level"
                        min={90}
                        max={99.9}
                        step={0.1}
                        value={[serviceLevel]}
                        onValueChange={(values) => setServiceLevel(values[0])}
                      />
                      <p className="text-xs text-muted-foreground">
                        Higher service level reduces stockouts but increases holding costs
                      </p>
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="lead-time">Lead Time (days)</Label>
                      <Input
                        id="lead-time"
                        type="number"
                        min={1}
                        placeholder={`Default: ${selectedProduct.lead_time || 7} days`}
                        value={customLeadTime !== null ? customLeadTime : ''}
                        onChange={(e) => {
                          const value = e.target.value ? parseInt(e.target.value) : null;
                          setCustomLeadTime(value);
                        }}
                      />
                      <p className="text-xs text-muted-foreground">
                        Time from order placement to receiving inventory
                      </p>
                    </div>
                    
                    <Button 
                      className="w-full mt-4" 
                      onClick={handleOptimize}
                      disabled={isOptimizing}
                    >
                      {isOptimizing ? (
                        <>Optimizing <RefreshCcw className="ml-2 h-4 w-4 animate-spin" /></>
                      ) : (
                        <>Optimize Stock Levels <Calculator className="ml-2 h-4 w-4" /></>
                      )}
                    </Button>
                  </>
                )}
              </div>
              
              <div className="bg-slate-50 rounded-lg p-4 space-y-2">
                <h3 className="font-medium flex items-center">
                  <Package className="h-4 w-4 mr-2" />
                  Current Inventory Status
                </h3>
                
                {selectedProduct ? (
                  <div className="space-y-3">
                    <div className="grid grid-cols-2 gap-2">
                      <div className="bg-white rounded p-2 shadow-sm">
                        <p className="text-sm text-muted-foreground">Current Stock</p>
                        <p className="text-xl font-bold">{selectedProduct.current_stock}</p>
                      </div>
                      <div className="bg-white rounded p-2 shadow-sm">
                        <p className="text-sm text-muted-foreground">Reorder Point</p>
                        <p className="text-xl font-bold">{selectedProduct.reorder_point}</p>
                      </div>
                      <div className="bg-white rounded p-2 shadow-sm">
                        <p className="text-sm text-muted-foreground">Optimal Stock</p>
                        <p className="text-xl font-bold">{selectedProduct.optimal_stock || 'Not set'}</p>
                      </div>
                      <div className="bg-white rounded p-2 shadow-sm">
                        <p className="text-sm text-muted-foreground">Lead Time</p>
                        <p className="text-xl font-bold">{selectedProduct.lead_time || 7} days</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-center p-2 bg-white rounded shadow-sm">
                      <p className="text-sm">
                        <span className="font-semibold">Status:</span> {' '}
                        <span className={`${
                          selectedProduct.stock_status === 'adequate' ? 'text-green-600' :
                          selectedProduct.stock_status === 'low_stock' ? 'text-amber-600' :
                          selectedProduct.stock_status === 'out_of_stock' ? 'text-red-600' :
                          'text-blue-600'
                        }`}>
                          {selectedProduct.stock_status.replace('_', ' ')}
                        </span>
                      </p>
                    </div>
                  </div>
                ) : (
                  <p className="text-muted-foreground">Select a product to view details</p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
        
        {optimizationResult && selectedProduct && (
          <>
            <Card>
              <CardHeader>
                <CardTitle>Optimization Results</CardTitle>
                <CardDescription>
                  Recommended inventory parameters for {selectedProduct.name}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <div>
                    <h3 className="text-lg font-medium mb-4">Recommended Parameters</h3>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="border rounded p-3">
                        <p className="text-sm text-muted-foreground">Safety Stock</p>
                        <div className="flex items-center justify-between">
                          <p className="text-2xl font-bold">{optimizationResult.safety_stock}</p>
                          {optimizationResult.safety_stock > (selectedProduct.reorder_point - (optimizationResult.avg_daily_demand * optimizationResult.lead_time)) ? (
                            <ArrowRight className="h-5 w-5 text-green-500" />
                          ) : (
                            <ArrowRight className="h-5 w-5 text-red-500 transform rotate-180" />
                          )}
                        </div>
                      </div>
                      
                      <div className="border rounded p-3">
                        <p className="text-sm text-muted-foreground">Reorder Point</p>
                        <div className="flex items-center justify-between">
                          <p className="text-2xl font-bold">{optimizationResult.reorder_point}</p>
                          {optimizationResult.reorder_point > selectedProduct.reorder_point ? (
                            <ArrowRight className="h-5 w-5 text-green-500" />
                          ) : (
                            <ArrowRight className="h-5 w-5 text-red-500 transform rotate-180" />
                          )}
                        </div>
                      </div>
                      
                      <div className="border rounded p-3">
                        <p className="text-sm text-muted-foreground">Order Quantity</p>
                        <p className="text-2xl font-bold">{optimizationResult.economic_order_quantity}</p>
                      </div>
                      
                      <div className="border rounded p-3">
                        <p className="text-sm text-muted-foreground">Optimal Stock</p>
                        <div className="flex items-center justify-between">
                          <p className="text-2xl font-bold">{optimizationResult.optimal_stock}</p>
                          {optimizationResult.optimal_stock > (selectedProduct.optimal_stock || 0) ? (
                            <ArrowRight className="h-5 w-5 text-green-500" />
                          ) : (
                            <ArrowRight className="h-5 w-5 text-red-500 transform rotate-180" />
                          )}
                        </div>
                      </div>
                    </div>
                    
                    <div className="mt-6 border rounded p-4 bg-slate-50">
                      <h4 className="font-medium mb-2">Optimization Factors</h4>
                      <Table>
                        <TableBody>
                          <TableRow>
                            <TableCell className="font-medium">Avg. Daily Demand</TableCell>
                            <TableCell>{optimizationResult.avg_daily_demand.toFixed(1)} units</TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell className="font-medium">Demand Variability</TableCell>
                            <TableCell>±{optimizationResult.demand_variability.toFixed(1)} units</TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell className="font-medium">Service Level</TableCell>
                            <TableCell>{(optimizationResult.service_level * 100).toFixed(1)}%</TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell className="font-medium">Lead Time</TableCell>
                            <TableCell>{optimizationResult.lead_time} days</TableCell>
                          </TableRow>
                        </TableBody>
                      </Table>
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="text-lg font-medium mb-4">Parameter Comparison</h3>
                    <div className="h-64 mb-6">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart
                          data={generateComparisonData()}
                          layout="vertical"
                          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                        >
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis type="number" />
                          <YAxis type="category" dataKey="name" />
                          <Tooltip />
                          <Legend />
                          <Bar dataKey="reorderPoint" name="Reorder Point" fill="#8884d8" />
                          <Bar dataKey="optimalStock" name="Optimal Stock" fill="#82ca9d" />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                    
                    <h3 className="text-lg font-medium mb-4">Cost Analysis</h3>
                    {optimizationResult.cost_analysis && (
                      <>
                        <div className="h-64">
                          <ResponsiveContainer width="100%" height="100%">
                            <BarChart
                              data={generateComparisonData()}
                              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                            >
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey="name" />
                              <YAxis />
                              <Tooltip />
                              <Legend />
                              <Bar dataKey="holdingCost" name="Holding Cost" fill="#8884d8" />
                              <Bar dataKey="stockoutCost" name="Stockout Cost" fill="#ff7675" />
                            </BarChart>
                          </ResponsiveContainer>
                        </div>
                        
                        <div className="mt-4 border rounded-lg p-4 bg-green-50 text-green-800">
                          <div className="flex items-center">
                            <TrendingUp className="h-5 w-5 mr-2" />
                            <h4 className="font-medium">Potential Savings</h4>
                          </div>
                          <p className="mt-2">
                            Optimized inventory parameters could save approximately {' '}
                            <span className="font-bold">
                              ${optimizationResult.cost_analysis.potential_savings.toFixed(2)}
                            </span>
                            {' '} ({optimizationResult.cost_analysis.savings_percent.toFixed(1)}%)
                            in inventory costs.
                          </p>
                        </div>
                      </>
                    )}
                  </div>
                </div>
              </CardContent>
              <CardFooter className="flex justify-end">
                <Button variant="outline" onClick={resetOptimization}>
                  Reset
                </Button>
              </CardFooter>
            </Card>
          </>
        )}
      </div>
    </div>
  );
};

export default StockOptimizer;
