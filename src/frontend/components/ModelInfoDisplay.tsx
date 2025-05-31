"use client"

import { useState, useEffect } from "react"
import axios from "axios"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { BarChart3, Database, Settings, TrendingUp } from "lucide-react"

interface ModelInfo {
  feature_importances: Record<string, number>
  model_type: string
  status: string
  model_metrics: {
    mae: number
    mse: number
    rmse: number
    r2: number
    training_samples: number
    test_samples: number
  }
  data_summary: {
    total_records: number
    avg_price: number
    min_price: number
    max_price: number
    property_types: Record<string, number>
    dublin_areas: Record<string, number>
  }
  available_options: {
    property_types: string[]
    dublin_areas: number[]
  }
}

export default function ModelInfoDisplay() {
  const [modelInfo, setModelInfo] = useState<ModelInfo | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchModelInfo = async () => {
      try {
        setIsLoading(true)
        const response = await axios.get("http://localhost:8000/model-info")
        setModelInfo(response.data)
        setError(null)
      } catch (err) {
        console.error("Error fetching model info:", err)
        setError("Failed to load model information")
      } finally {
        setIsLoading(false)
      }
    }

    fetchModelInfo()
  }, [])

  if (isLoading) {
    return (
      <div className="space-y-8">
        <Card className="shadow-lg">
          <CardContent className="p-8">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Loading model information...</p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-8">
        <Card className="shadow-lg border-red-200 bg-red-50">
          <CardContent className="p-8">
            <div className="text-center">
              <p className="text-red-600">{error}</p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (!modelInfo) {
    return null
  }

  // Sort feature importances by value (descending)
  const sortedFeatures = Object.entries(modelInfo.feature_importances)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 10) // Show top 10 features

  return (
    <div className="space-y-8 mt-8">
      {/* Model Status */}
      <Card className="shadow-lg">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Model Status
          </CardTitle>
          <CardDescription>Current model information and status</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <Badge variant="secondary" className="mb-2">
                {modelInfo.model_type}
              </Badge>
              <p className="text-sm text-gray-600">Model Type</p>
            </div>
            <div className="text-center">
              <Badge variant={modelInfo.status === "ML model active" ? "default" : "destructive"} className="mb-2">
                {modelInfo.status}
              </Badge>
              <p className="text-sm text-gray-600">Status</p>
            </div>
            <div className="text-center">
              <Badge variant="outline" className="mb-2">
                {modelInfo.data_summary.total_records} Records
              </Badge>
              <p className="text-sm text-gray-600">Training Data</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Model Performance Metrics */}
      <Card className="shadow-lg">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Model Performance
          </CardTitle>
          <CardDescription>Key metrics showing how well the model performs</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {(modelInfo.model_metrics.r2 * 100).toFixed(1)}%
              </div>
              <p className="text-sm text-gray-600 mt-1">R² Score</p>
              <p className="text-xs text-gray-500">Variance Explained</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                €{Math.round(modelInfo.model_metrics.mae)}
              </div>
              <p className="text-sm text-gray-600 mt-1">Mean Absolute Error</p>
              <p className="text-xs text-gray-500">Average Prediction Error</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {modelInfo.model_metrics.training_samples}
              </div>
              <p className="text-sm text-gray-600 mt-1">Training Samples</p>
              <p className="text-xs text-gray-500">80% of Data</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">
                {modelInfo.model_metrics.test_samples}
              </div>
              <p className="text-sm text-gray-600 mt-1">Test Samples</p>
              <p className="text-xs text-gray-500">20% of Data</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Feature Importances */}
      <Card className="shadow-lg">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Feature Importance
          </CardTitle>
          <CardDescription>Which factors most influence rent predictions</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {sortedFeatures.map(([feature, importance], index) => (
              <div key={feature} className="flex items-center space-x-4">
                <div className="w-4 text-sm text-gray-500 font-mono">
                  {index + 1}
                </div>
                <div className="flex-1">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm font-medium capitalize">
                      {feature.replace(/_/g, ' ').replace('dublin area', 'Dublin')}
                    </span>
                    <span className="text-sm text-gray-600">
                      {(importance * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${importance * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Data Summary */}
      <Card className="shadow-lg">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            Training Data Summary
          </CardTitle>
          <CardDescription>Overview of the data used to train the model</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Price Statistics */}
            <div>
              <h4 className="font-semibold mb-4">Price Statistics</h4>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Average Price:</span>
                  <span className="font-medium">€{Math.round(modelInfo.data_summary.avg_price)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Minimum Price:</span>
                  <span className="font-medium">€{Math.round(modelInfo.data_summary.min_price)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Maximum Price:</span>
                  <span className="font-medium">€{Math.round(modelInfo.data_summary.max_price)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Total Records:</span>
                  <span className="font-medium">{modelInfo.data_summary.total_records}</span>
                </div>
              </div>
            </div>

            {/* Property Types */}
            <div>
              <h4 className="font-semibold mb-4">Property Types</h4>
              <div className="space-y-2">
                {Object.entries(modelInfo.data_summary.property_types)
                  .sort(([, a], [, b]) => b - a)
                  .map(([type, count]) => (
                    <div key={type} className="flex justify-between items-center">
                      <span className="text-gray-600 capitalize">{type}:</span>
                      <div className="flex items-center space-x-2">
                        <span className="font-medium">{count}</span>
                        <div className="w-16 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-green-600 h-2 rounded-full"
                            style={{
                              width: `${(count / modelInfo.data_summary.total_records) * 100}%`
                            }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          </div>

          {/* Dublin Areas */}
          <div className="mt-8">
            <h4 className="font-semibold mb-4">Dublin Areas Covered</h4>
            <div className="flex flex-wrap gap-2">
              {modelInfo.available_options.dublin_areas
                .sort((a, b) => a - b)
                .map((area) => (
                  <Badge key={area} variant="outline" className="text-xs">
                    Dublin {area}
                  </Badge>
                ))}
            </div>
            <p className="text-sm text-gray-600 mt-2">
              Model trained on {modelInfo.available_options.dublin_areas.length} Dublin postal areas
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
