
import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { ArrowUpRight, BrainCircuit, ChevronDown, ChevronUp, Cloud, Loader2, RefreshCcw, Settings, Sliders } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';

// Types
interface Product {
  id: number;
  name: string;
  sku: string;
  category: string;
}

interface PredictionData {
  date: string;
  predicted_demand: number;
  confidence_lower: number;
  confidence_upper: number;
  actual_demand?: number;
}

interface ExternalFactor {
  date: string;
  factor_name: string;
  factor_type: 'holiday' | 'weather' | 'promotion' | 'other';
  impact_level: number;
}

interface ModelEvaluation {
  model_name: string;
  accuracy: number;
  mae: number;
  mse: number;
  training_time: number;
  last_trained: string;
}

interface AIInsight {
  title: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
  confidence: number;
  recommendation?: string;
}

// Mock data fetching functions
const fetchProducts = async (): Promise<Product[]> => {
  return [
    { id: 1, name: "Premium Wireless Headphones", sku: "ELEC-101", category: "Electronics" },
    { id: 2, name: "Organic Cotton T-Shirt", sku: "CLOTH-202", category: "Clothing" },
    { id: 3, name: "Smart Watch Series 7", sku: "ELEC-305", category: "Electronics" },
    { id: 4, name: "Ergonomic Office Chair", sku: "HOME-118", category: "Home & Kitchen" },
    { id: 5, name: "Yoga Mat Pro", sku: "SPORT-423", category: "Sports & Outdoors" }
  ];
};

const fetchPredictions = async (productId: number, model: string): Promise<PredictionData[]> => {
  // Generate 30 days of predictions with different patterns based on product ID
  const data: PredictionData[] = [];
  const today = new Date();
  const baseValue = 20 + (productId * 5);
  const variance = 5 + (productId % 5);
  
  // Create different patterns based on model selected
  let amplitude = 10;
  let frequency = 0.2;
  let trend = 0.2;
  
  switch (model) {
    case 'prophet':
      amplitude = 8;
      frequency = 0.3;
      trend = 0.4;
      break;
    case 'lstm':
      amplitude = 12;
      frequency = 0.15;
      trend = 0.1;
      break;
    case 'ensemble':
      amplitude = 10;
      frequency = 0.25;
      trend = 0.3;
      break;
  }
  
  // Generate predictions for next 30 days
  for (let i = 0; i < 30; i++) {
    const date = new Date();
    date.setDate(today.getDate() + i);
    
    // Generate some seasonal pattern with trend
    const dayOfWeek = date.getDay();
    const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
    const seasonality = amplitude * Math.sin(i * frequency) + (isWeekend ? 5 : 0);
    const trendEffect = trend * i;
    
    const predictedDemand = Math.max(0, Math.round(baseValue + seasonality + trendEffect));
    const confidenceMargin = Math.round(predictedDemand * 0.2); // 20% confidence interval
    
    data.push({
      date: date.toISOString().split('T')[0],
      predicted_demand: predictedDemand,
      confidence_lower: Math.max(0, predictedDemand - confidenceMargin),
      confidence_upper: predictedDemand + confidenceMargin,
      // Add actual values for past dates (first 10 days as "historical" for comparison)
      actual_demand: i < 10 ? Math.round(predictedDemand * (0.85 + Math.random() * 0.3)) : undefined
    });
  }
  
  return data;
};

const fetchExternalFactors = async (startDate: string, endDate: string): Promise<ExternalFactor[]> => {
  // Generate sample external factors
  const factors: ExternalFactor[] = [];
  
  // Holidays
  factors.push({
    date: "2023-04-15",
    factor_name: "Easter Weekend",
    factor_type: "holiday",
    impact_level: 0.8
  });
  
  factors.push({
    date: "2023-05-01",
    factor_name: "Labor Day",
    factor_type: "holiday",
    impact_level: 0.6
  });
  
  // Weather events
  factors.push({
    date: "2023-04-20",
    factor_name: "Heavy Rain",
    factor_type: "weather",
    impact_level: -0.5
  });
  
  // Promotions
  factors.push({
    date: "2023-04-10",
    factor_name: "Spring Sale",
    factor_type: "promotion",
    impact_level: 0.9
  });
  
  factors.push({
    date: "2023-04-25",
    factor_name: "Flash Sale",
    factor_type: "promotion",
    impact_level: 0.7
  });
  
  return factors;
};

const fetchModelEvaluations = async (): Promise<ModelEvaluation[]> => {
  return [
    {
      model_name: "Prophet",
      accuracy: 0.86,
      mae: 4.2,
      mse: 27.5,
      training_time: 12.5,
      last_trained: "2023-04-05"
    },
    {
      model_name: "LSTM Neural Network",
      accuracy: 0.89,
      mae: 3.8,
      mse: 23.1,
      training_time: 45.2,
      last_trained: "2023-04-02"
    },
    {
      model_name: "Random Forest",
      accuracy: 0.82,
      mae: 5.1,
      mse: 35.6,
      training_time: 8.7,
      last_trained: "2023-04-07"
    },
    {
      model_name: "Ensemble Model",
      accuracy: 0.91,
      mae: 3.2,
      mse: 19.4,
      training_time: 68.3,
      last_trained: "2023-04-01"
    }
  ];
};

const fetchAIInsights = async (productId: number): Promise<AIInsight[]> => {
  // Generate different insights based on product ID
  const insights: AIInsight[] = [
    {
      title: "Seasonal Demand Pattern Detected",
      description: "This product shows a strong weekly seasonality with peaks on weekends.",
      impact: "high",
      confidence: 0.92,
      recommendation: "Consider adjusting staffing and inventory levels for weekend demand."
    },
    {
      title: "Weather Sensitivity",
      description: "Sales drop significantly during rainy days, especially for outdoor-related products.",
      impact: "medium",
      confidence: 0.78,
      recommendation: "Plan alternative promotions for poor weather conditions."
    }
  ];
  
  if (productId % 2 === 0) {
    insights.push({
      title: "Promotion Effectiveness",
      description: "Flash sales for this product category result in 40% higher sales compared to standard discounts.",
      impact: "high",
      confidence: 0.85,
      recommendation: "Prioritize flash sales over long-term discounts for this product."
    });
  } else {
    insights.push({
      title: "Price Elasticity",
      description: "This product shows high price elasticity. Small price reductions lead to significant sales increases.",
      impact: "high",
      confidence: 0.88,
      recommendation: "Consider strategic price reductions during slow periods."
    });
  }
  
  if (productId % 3 === 0) {
    insights.push({
      title: "Inventory Risk Alert",
      description: "Current stock levels may not be sufficient for predicted demand spikes in the next 2 weeks.",
      impact: "high",
      confidence: 0.81,
      recommendation: "Increase order quantity by 25% for next restock."
    });
  }
  
  return insights;
};

const AIPredictionEngine: React.FC = () => {
  const [selectedProductId, setSelectedProductId] = useState<number | null>(null);
  const [selectedModel, setSelectedModel] = useState<string>("ensemble");
  const [predictionHorizon, setPredictionHorizon] = useState<number>(30);
  const [isTraining, setIsTraining] = useState<boolean>(false);
  const [includeExternalFactors, setIncludeExternalFactors] = useState<boolean>(true);
  const [confidenceLevel, setConfidenceLevel] = useState<number>(90);
  
  // Fetch products
  const { data: products, isLoading: productsLoading } = useQuery({
    queryKey: ['predictionProducts'],
    queryFn: fetchProducts
  });
  
  // Fetch predictions when product or model changes
  const { data: predictions, isLoading: predictionsLoading, refetch: refetchPredictions } = useQuery({
    queryKey: ['predictions', selectedProductId, selectedModel, predictionHorizon],
    queryFn: () => selectedProductId ? fetchPredictions(selectedProductId, selectedModel) : Promise.resolve([]),
    enabled: !!selectedProductId
  });
  
  // Fetch external factors
  const { data: externalFactors, isLoading: factorsLoading } = useQuery({
    queryKey: ['externalFactors'],
    queryFn: () => fetchExternalFactors("2023-04-01", "2023-05-30"),
    enabled: includeExternalFactors
  });
  
  // Fetch model evaluations
  const { data: modelEvaluations, isLoading: evaluationsLoading } = useQuery({
    queryKey: ['modelEvaluations'],
    queryFn: fetchModelEvaluations
  });
  
  // Fetch AI insights
  const { data: aiInsights, isLoading: insightsLoading } = useQuery({
    queryKey: ['aiInsights', selectedProductId],
    queryFn: () => selectedProductId ? fetchAIInsights(selectedProductId) : Promise.resolve([]),
    enabled: !!selectedProductId
  });
  
  // Handle model training simulation
  const handleTrainModel = () => {
    setIsTraining(true);
    
    // Simulate training process
    setTimeout(() => {
      setIsTraining(false);
      refetchPredictions();
    }, 3000);
  };
  
  // Find selected product
  const selectedProduct = products?.find(p => p.id === selectedProductId);
  
  // Selected model details
  const selectedModelDetails = modelEvaluations?.find(model => model.model_name.toLowerCase().includes(selectedModel));
  
  return (
    <div className="container mx-auto py-6">
      <div className="flex flex-col gap-6">
        <h1 className="text-3xl font-bold flex items-center">
          <BrainCircuit className="mr-2 h-8 w-8 text-purple-500" />
          AI Demand Prediction Engine
        </h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Configuration Panel */}
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle>Model Configuration</CardTitle>
              <CardDescription>
                Configure AI prediction parameters
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="product-select">Select Product</Label>
                <Select
                  value={selectedProductId?.toString() || ""}
                  onValueChange={(value) => setSelectedProductId(Number(value))}
                >
                  <SelectTrigger id="product-select">
                    <SelectValue placeholder="Select a product" />
                  </SelectTrigger>
                  <SelectContent>
                    {productsLoading ? (
                      <SelectItem value="loading" disabled>Loading products...</SelectItem>
                    ) : products && products.length > 0 ? (
                      products.map(product => (
                        <SelectItem key={product.id} value={product.id.toString()}>
                          {product.name}
                        </SelectItem>
                      ))
                    ) : (
                      <SelectItem value="none" disabled>No products available</SelectItem>
                    )}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="model-select">Prediction Model</Label>
                <Select
                  value={selectedModel}
                  onValueChange={setSelectedModel}
                >
                  <SelectTrigger id="model-select">
                    <SelectValue placeholder="Select a model" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="prophet">Prophet</SelectItem>
                    <SelectItem value="lstm">LSTM Neural Network</SelectItem>
                    <SelectItem value="randomforest">Random Forest</SelectItem>
                    <SelectItem value="ensemble">Ensemble Model</SelectItem>
                  </SelectContent>
                </Select>
                {selectedModelDetails && (
                  <div className="text-xs text-muted-foreground mt-1">
                    Accuracy: {(selectedModelDetails.accuracy * 100).toFixed(1)}% • 
                    MAE: {selectedModelDetails.mae.toFixed(1)} • 
                    Last trained: {selectedModelDetails.last_trained}
                  </div>
                )}
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between">
                  <Label htmlFor="prediction-horizon">
                    Prediction Horizon: {predictionHorizon} days
                  </Label>
                </div>
                <Slider
                  id="prediction-horizon"
                  min={7}
                  max={90}
                  step={1}
                  value={[predictionHorizon]}
                  onValueChange={(values) => setPredictionHorizon(values[0])}
                />
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between">
                  <Label htmlFor="confidence-level">
                    Confidence Level: {confidenceLevel}%
                  </Label>
                </div>
                <Slider
                  id="confidence-level"
                  min={70}
                  max={99}
                  step={1}
                  value={[confidenceLevel]}
                  onValueChange={(values) => setConfidenceLevel(values[0])}
                />
                <div className="text-xs text-muted-foreground">
                  Higher confidence levels result in wider prediction intervals
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <Switch
                  id="external-factors"
                  checked={includeExternalFactors}
                  onCheckedChange={setIncludeExternalFactors}
                />
                <Label htmlFor="external-factors">Include External Factors</Label>
              </div>
              
              <Button 
                className="w-full" 
                onClick={handleTrainModel}
                disabled={isTraining || !selectedProductId}
              >
                {isTraining ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Training Model...
                  </>
                ) : (
                  <>
                    <RefreshCcw className="mr-2 h-4 w-4" />
                    {selectedProductId ? "Retrain Model" : "Select a Product"}
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
          
          {/* Prediction Results */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>
                {selectedProduct ? `Demand Predictions: ${selectedProduct.name}` : 'Demand Predictions'}
              </CardTitle>
              <CardDescription>
                AI-powered demand forecasts with confidence intervals
              </CardDescription>
            </CardHeader>
            <CardContent>
              {!selectedProductId ? (
                <div className="flex flex-col items-center justify-center h-64 text-center">
                  <Cloud className="h-16 w-16 text-muted-foreground mb-4" />
                  <h3 className="text-lg font-medium">Select a Product</h3>
                  <p className="text-sm text-muted-foreground max-w-md">
                    Choose a product from the configuration panel to see AI-powered demand predictions.
                  </p>
                </div>
              ) : predictionsLoading || isTraining ? (
                <div className="flex items-center justify-center h-64">
                  <Loader2 className="h-8 w-8 text-primary animate-spin mr-2" />
                  <p>{isTraining ? "Training model..." : "Loading predictions..."}</p>
                </div>
              ) : predictions && predictions.length > 0 ? (
                <div className="h-96">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart
                      data={predictions}
                      margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
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
                      <YAxis />
                      <Tooltip 
                        labelFormatter={(label) => {
                          const date = new Date(label);
                          return date.toLocaleDateString();
                        }}
                      />
                      <Legend />
                      <Area 
                        type="monotone" 
                        dataKey="confidence_upper" 
                        stackId="1" 
                        stroke="transparent" 
                        fill="rgba(136, 132, 216, 0.2)" 
                        name="Upper Bound" 
                      />
                      <Area 
                        type="monotone" 
                        dataKey="predicted_demand" 
                        stackId="2" 
                        stroke="#8884d8" 
                        fill="#8884d8" 
                        name="Predicted Demand" 
                      />
                      <Area 
                        type="monotone" 
                        dataKey="confidence_lower" 
                        stackId="3" 
                        stroke="transparent" 
                        fill="rgba(136, 132, 216, 0.2)" 
                        name="Lower Bound" 
                      />
                      <Line 
                        type="monotone" 
                        dataKey="actual_demand" 
                        stroke="#82ca9d" 
                        strokeWidth={2} 
                        dot={{ r: 4 }}
                        activeDot={{ r: 6 }}
                        name="Actual Demand" 
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <p>No prediction data available.</p>
              )}
              
              {/* External factors that influence predictions */}
              {selectedProductId && includeExternalFactors && (
                <div className="mt-6">
                  <h3 className="text-lg font-medium mb-4">External Factors</h3>
                  {factorsLoading ? (
                    <div className="flex items-center justify-center h-16">
                      <Loader2 className="h-5 w-5 text-primary animate-spin mr-2" />
                      <p>Loading factors...</p>
                    </div>
                  ) : externalFactors && externalFactors.length > 0 ? (
                    <div className="flex flex-wrap gap-2">
                      {externalFactors.map((factor, i) => (
                        <div 
                          key={`${factor.date}-${i}`}
                          className={`px-3 py-1.5 rounded-lg text-sm flex items-center ${
                            factor.factor_type === 'holiday' ? 'bg-blue-100 text-blue-800 border border-blue-200' :
                            factor.factor_type === 'weather' ? 'bg-amber-100 text-amber-800 border border-amber-200' :
                            factor.factor_type === 'promotion' ? 'bg-green-100 text-green-800 border border-green-200' :
                            'bg-gray-100 text-gray-800 border border-gray-200'
                          }`}
                        >
                          <span className="font-medium">{factor.factor_name}</span>
                          <span className="ml-2 text-xs">
                            {new Date(factor.date).toLocaleDateString()}
                          </span>
                          <span className={`ml-2 ${
                            factor.impact_level > 0.5 ? 'text-green-600' :
                            factor.impact_level > 0 ? 'text-green-500' :
                            factor.impact_level > -0.5 ? 'text-red-500' : 'text-red-600'
                          }`}>
                            {factor.impact_level > 0 ? `+${(factor.impact_level * 100).toFixed(0)}%` : `${(factor.impact_level * 100).toFixed(0)}%`}
                          </span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-muted-foreground">No external factors found for this time period.</p>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
        
        {/* AI Insights and Model Analytics */}
        <Tabs defaultValue="insights" className="w-full">
          <TabsList className="grid w-full md:w-[400px] grid-cols-2">
            <TabsTrigger value="insights">AI Insights</TabsTrigger>
            <TabsTrigger value="analytics">Model Analytics</TabsTrigger>
          </TabsList>
          
          {/* AI Insights Tab */}
          <TabsContent value="insights">
            <Card>
              <CardHeader>
                <CardTitle>AI-Generated Insights</CardTitle>
                <CardDescription>
                  Automatically generated insights based on demand patterns
                </CardDescription>
              </CardHeader>
              <CardContent>
                {!selectedProductId ? (
                  <div className="flex items-center justify-center h-32 text-center">
                    <p className="text-muted-foreground">Select a product to view AI insights</p>
                  </div>
                ) : insightsLoading ? (
                  <div className="flex items-center justify-center h-32">
                    <Loader2 className="h-5 w-5 text-primary animate-spin mr-2" />
                    <p>Analyzing patterns...</p>
                  </div>
                ) : aiInsights && aiInsights.length > 0 ? (
                  <div className="grid gap-4">
                    {aiInsights.map((insight, index) => (
                      <div key={index} className="border rounded-lg p-4">
                        <div className="flex items-start justify-between">
                          <h3 className="font-semibold flex items-center">
                            {insight.title}
                            <Badge 
                              variant="outline"
                              className={`ml-2 ${
                                insight.impact === 'high' ? 'bg-red-100 text-red-800' :
                                insight.impact === 'medium' ? 'bg-amber-100 text-amber-800' :
                                'bg-blue-100 text-blue-800'
                              }`}
                            >
                              {insight.impact} impact
                            </Badge>
                          </h3>
                          <Badge variant="secondary">
                            {(insight.confidence * 100).toFixed(0)}% confidence
                          </Badge>
                        </div>
                        <p className="text-muted-foreground mt-2">
                          {insight.description}
                        </p>
                        {insight.recommendation && (
                          <div className="mt-3 p-2 bg-muted rounded border border-border">
                            <p className="text-sm font-medium">Recommendation:</p>
                            <p className="text-sm">{insight.recommendation}</p>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p>No insights available for this product.</p>
                )}
              </CardContent>
            </Card>
          </TabsContent>
          
          {/* Model Analytics Tab */}
          <TabsContent value="analytics">
            <Card>
              <CardHeader>
                <CardTitle>Model Performance Analytics</CardTitle>
                <CardDescription>
                  Comparison of different prediction models
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="text-lg font-medium mb-4">Model Evaluation</h3>
                    {evaluationsLoading ? (
                      <div className="flex items-center justify-center h-32">
                        <Loader2 className="h-5 w-5 text-primary animate-spin mr-2" />
                        <p>Loading evaluations...</p>
                      </div>
                    ) : (
                      <div className="rounded-md border">
                        <Table>
                          <TableHeader>
                            <TableRow>
                              <TableHead>Model</TableHead>
                              <TableHead className="text-right">Accuracy</TableHead>
                              <TableHead className="text-right">MAE</TableHead>
                              <TableHead className="text-right">MSE</TableHead>
                              <TableHead className="text-right">Training Time</TableHead>
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            {modelEvaluations?.map(model => (
                              <TableRow 
                                key={model.model_name}
                                className={selectedModel === model.model_name.toLowerCase().split(' ')[0].toLowerCase() ? 'bg-muted/40' : ''}
                              >
                                <TableCell className="font-medium">{model.model_name}</TableCell>
                                <TableCell className="text-right">{(model.accuracy * 100).toFixed(1)}%</TableCell>
                                <TableCell className="text-right">{model.mae.toFixed(1)}</TableCell>
                                <TableCell className="text-right">{model.mse.toFixed(1)}</TableCell>
                                <TableCell className="text-right">{model.training_time.toFixed(1)}s</TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </div>
                    )}
                  </div>
                  
                  <div>
                    <h3 className="text-lg font-medium mb-4">Model Comparison</h3>
                    {evaluationsLoading ? (
                      <div className="flex items-center justify-center h-32">
                        <Loader2 className="h-5 w-5 text-primary animate-spin mr-2" />
                        <p>Loading comparison...</p>
                      </div>
                    ) : (
                      <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart
                            data={modelEvaluations?.map(model => ({
                              name: model.model_name.replace(' Neural Network', '').replace(' Model', ''),
                              accuracy: Math.round(model.accuracy * 100),
                              mae: model.mae,
                              mse: model.mse / 10 // Scale down MSE for better visualization
                            }))}
                            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                          >
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="name" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Bar dataKey="accuracy" name="Accuracy (%)" fill="#8884d8" />
                            <Bar dataKey="mae" name="MAE" fill="#82ca9d" />
                            <Bar dataKey="mse" name="MSE (÷10)" fill="#ffc658" />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    )}
                    
                    <div className="mt-4 p-3 bg-muted/50 rounded-lg">
                      <h4 className="font-medium mb-1">Model Selection Guide</h4>
                      <ul className="text-sm space-y-1">
                        <li>• <span className="font-medium">Prophet</span>: Best for seasonal patterns with weekly and yearly cycles</li>
                        <li>• <span className="font-medium">LSTM</span>: Best for long-term dependencies and complex patterns</li>
                        <li>• <span className="font-medium">Random Forest</span>: Strong with external factors and categorical features</li>
                        <li>• <span className="font-medium">Ensemble</span>: Combines strengths of all models for highest accuracy</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </CardContent>
              <CardFooter className="flex justify-end">
                <Button variant="outline" size="sm" className="text-xs">
                  <Settings className="mr-1 h-3 w-3" />
                  Advanced Settings
                </Button>
              </CardFooter>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default AIPredictionEngine;
