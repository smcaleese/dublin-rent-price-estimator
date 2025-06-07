export interface SearchHistoryItem {
  id: number;
  user_id: number;
  search_parameters: {
    bedrooms?: string | null;
    bathrooms?: string | null;
    propertyType: string;
    dublinArea: string;
    isShared?: boolean | null;
    roomType?: string | null;
    // Add any other parameters that might be part of a search in the future
  };
  prediction_result: {
    predictedPrice: number;
    lowerBound: number;
    upperBound: number;
  };
  timestamp: string; // ISO date string from JSON
}
