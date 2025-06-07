"use client"

import { useState, FormEvent } from "react"
// import { useRouter } from "next/navigation" // No longer needed as AuthContext handles navigation
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
// import axios from "axios" // No longer directly needed here
import { useAuth } from "@/context/AuthContext" // Import useAuth

export default function SignUpPage() {
  const { signup } = useAuth() // Get signup function from context
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  // const router = useRouter() // No longer needed

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setError(null)
    setIsLoading(true)

    try {
      await signup(email, password)
      // Navigation to /login?signup=success is handled by the signup function in AuthContext
    } catch (err: any) {
      // AuthContext's signup function re-throws the error
      if (err.response && err.response.data && err.response.data.detail) {
        setError(err.response.data.detail)
      } else if (err.message) {
        setError(err.message)
      } else {
        setError("Sign up failed. Please try again later.")
      }
      console.error("Sign up page error:", err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen py-2">
      <main className="flex flex-col items-center justify-center w-full flex-1 px-4 sm:px-20 text-center">
        <h1 className="text-4xl font-bold mb-8">Create Account</h1>
        <form
          onSubmit={handleSubmit}
          className="w-full max-w-md bg-white p-8 rounded-lg shadow-md"
        >
          {error && <p className="text-red-500 mb-4">{error}</p>}
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
          <Button type="submit" className="w-full bg-green-600 hover:bg-green-700 text-white" disabled={isLoading}>
            {isLoading ? "Creating Account..." : "Create Account"}
          </Button>
        </form>
      </main>
    </div>
  )
}
