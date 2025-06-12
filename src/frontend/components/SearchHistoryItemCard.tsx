"use client"

import React from "react"
import { SearchHistoryItem } from "../lib/types"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "./ui/card"

interface SearchHistoryItemCardProps {
  item: SearchHistoryItem
}

const SearchHistoryItemCard: React.FC<SearchHistoryItemCardProps> = ({ item }) => {
  const { search_parameters, prediction_result } = item

  // Helper to format parameters for display
  const formatParameters = (params: typeof search_parameters) => {
    const parts = []
    if (params.propertyType) parts.push(`Type: ${params.propertyType}`)
    if (params.dublinArea) parts.push(`Area: ${params.dublinArea}`)
    if (params.isShared) {
      parts.push(`Shared: Yes`)
      if (params.roomType) parts.push(`Room: ${params.roomType}`)
    } else {
      if (params.bedrooms) parts.push(`Beds: ${params.bedrooms}`)
      if (params.bathrooms) parts.push(`Baths: ${params.bathrooms}`)
    }
    return parts.join(", ")
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardDescription>{formatParameters(search_parameters)}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-1">
          <p className="font-semibold">Predicted Rent:</p>
          <p className="text-lg">€{prediction_result.predictedPrice.toLocaleString()}</p>
          <p className="text-sm text-gray-600">
            Range: €{prediction_result.lowerBound.toLocaleString()} - €{prediction_result.upperBound.toLocaleString()}
          </p>
        </div>
      </CardContent>
    </Card>
  )
}

export default SearchHistoryItemCard
