"use client";

import React, { useEffect, useState } from "react"
import { useAuth } from "../../context/AuthContext"
import { fetchUserSearchHistory } from "../../lib/utils"
import { SearchHistoryItem } from "../../lib/types"
import SearchHistoryItemCard from "../../components/SearchHistoryItemCard"

const SearchHistoryPage = () => {
  const { user, token, isLoading: authLoading } = useAuth()
  const [historyItems, setHistoryItems] = useState<SearchHistoryItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (authLoading) {
      // Wait for authentication status to be resolved
      return
    }

    if (!user || !token) {
      setError("Please log in to view your search history.")
      setIsLoading(false)
      return
    }

    const loadHistory = async () => {
      setIsLoading(true)
      setError(null)
      try {
        const data = await fetchUserSearchHistory(token)
        setHistoryItems(data)
      } catch (err) {
        if (err instanceof Error) {
          setError(err.message)
        } else {
          setError("An unknown error occurred.")
        }
      } finally {
        setIsLoading(false)
      }
    }

    loadHistory()
  }, [user, token, authLoading])

  if (isLoading || authLoading) {
    return <div className="container mx-auto p-4 text-center">Loading search history...</div>
  }

  if (error) {
    return <div className="container mx-auto p-4 text-center text-red-500">Error: {error}</div>
  }

  if (historyItems.length === 0) {
    return <div className="container mx-auto p-4 text-center">You have no search history yet.</div>
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6 text-center">Your Search History</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {historyItems.map((item) => (
          <SearchHistoryItemCard key={item.id} item={item} />
        ))}
      </div>
    </div>
  )
}

export default SearchHistoryPage
