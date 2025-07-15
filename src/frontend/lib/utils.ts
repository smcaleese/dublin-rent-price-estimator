import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Import the SearchHistoryItem type
import { SearchHistoryItem } from "./types"

export async function fetchUserSearchHistory(token: string): Promise<SearchHistoryItem[]> {
  const backendUrl = process.env.NEXT_PUBLIC_API_URL
  const endpoint = `${backendUrl}/users/me/search-history`

  try {
    const response = await fetch(endpoint, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      // Try to parse error response from backend
      let errorDetail = "Failed to fetch search history."
      try {
        const errorData = await response.json()
        if (errorData && errorData.detail) {
          errorDetail = errorData.detail
        }
      } catch (e) {
        // Ignore if error response is not JSON
      }
      throw new Error(errorDetail)
    }

    const data: SearchHistoryItem[] = await response.json()
    return data
  } catch (error) {
    console.error("Error fetching search history:", error)
    // Re-throw the error so the calling component can handle it
    if (error instanceof Error) {
      throw error
    }
    throw new Error("An unknown error occurred while fetching search history.")
  }
}
