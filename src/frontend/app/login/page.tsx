"use client"

import { useState, FormEvent, useEffect } from "react"
import { useRouter, useSearchParams } from "next/navigation" // Keep useRouter for now, though AuthContext might handle all nav
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
// import axios from "axios" // Will be removed as useAuth handles it
import { useAuth } from "@/context/AuthContext" // Import useAuth

export default function LoginPage() {
  const { login } = useAuth() // Get login function from context
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()
  const searchParams = useSearchParams()

  useEffect(() => {
    if (searchParams.get("signup") === "success") {
      setSuccessMessage("Account created successfully! Please log in.")
    }
    if (searchParams.get("session_expired") === "true") {
      setError("Your session has expired. Please log in again.")
    }
  }, [searchParams])

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setError(null)
    setSuccessMessage(null)
    setIsLoading(true)

    try {
      await login(email, password)
      // Navigation is handled by the login function in AuthContext
    } catch (err: any) {
      // AuthContext's login function re-throws the error, so catch it here for UI feedback
      if (err.response && err.response.data && err.response.data.detail) {
        setError(err.response.data.detail)
      } else if (err.message) {
        setError(err.message) // For generic errors thrown by AuthContext
      } else {
        setError("Log in failed. Please check your credentials or try again later.")
      }
      console.error("Login page error:", err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen py-2">
      <main className="flex flex-col items-center justify-center w-full flex-1 px-4 sm:px-20 text-center">
        <h1 className="text-4xl font-bold mb-8">Log In</h1>
        <form
          onSubmit={handleSubmit}
          className="w-full max-w-md bg-white p-8 rounded-lg shadow-md"
        >
          {error && <p className="text-red-500 mb-4">{error}</p>}
          {successMessage && <p className="text-green-500 mb-4">{successMessage}</p>}
          <div className="mb-6 text-left">
            <Label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
              Email Address
            </Label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              placeholder="you@example.com"
            />
          </div>
          <div className="mb-6 text-left">
            <Label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </Label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              placeholder="••••••••"
            />
          </div>
          <Button type="submit" className="w-full bg-indigo-600 hover:bg-indigo-700 text-white" disabled={isLoading}>
            {isLoading ? "Logging In..." : "Log In"}
          </Button>
        </form>
      </main>
    </div>
  )
}
