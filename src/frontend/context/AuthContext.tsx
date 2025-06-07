"use client"

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react"
import axios from "axios"
import { useRouter } from "next/navigation"

interface User {
  id: number
  email: string
}

interface AuthContextType {
  user: User | null
  token: string | null
  isLoading: boolean
  login: (email_or_username: string, password_string: string) => Promise<void>
  signup: (email_string: string, password_string: string) => Promise<void>
  logout: () => void
  fetchUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true) // Start true to check for token
  const router = useRouter()

  const API_URL = "http://localhost:8000"

  const fetchUser = async (currentToken?: string) => {
    const tokenToUse = currentToken || token
    if (tokenToUse) {
      try {
        const response = await axios.get(`${API_URL}/users/me`, {
          headers: { Authorization: `Bearer ${tokenToUse}` },
        })
        setUser(response.data)
      } catch (error) {
        console.error("Failed to fetch user", error)
        // Token might be invalid/expired
        setUser(null)
        setToken(null)
        localStorage.removeItem("accessToken")
        // Optionally redirect to login if on a protected route
        // router.push("/login?session_expired=true"); 
      }
    }
    setIsLoading(false)
  }

  useEffect(() => {
    const storedToken = localStorage.getItem("accessToken")
    if (storedToken) {
      setToken(storedToken)
      axios.defaults.headers.common["Authorization"] = `Bearer ${storedToken}`
      fetchUser(storedToken)
    } else {
      setIsLoading(false)
    }
  }, [])


  const login = async (email_or_username: string, password_string: string) => {
    setIsLoading(true)
    try {
      const formData = new URLSearchParams()
      formData.append("username", email_or_username)
      formData.append("password", password_string)

      const response = await axios.post(`${API_URL}/login`, formData, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      })
      
      const new_token = response.data.access_token
      setToken(new_token)
      localStorage.setItem("accessToken", new_token)
      axios.defaults.headers.common["Authorization"] = `Bearer ${new_token}`
      await fetchUser(new_token) // Fetch user info after login
      router.push("/")
    } catch (error) {
      console.error("Login failed", error)
      setIsLoading(false)
      throw error // Re-throw to be caught by the form
    }
  }

  const signup = async (email_string: string, password_string: string) => {
    setIsLoading(true)
    try {
      await axios.post(`${API_URL}/signup`, { email: email_string, password: password_string })
      // After signup, typically redirect to login or show success message
      router.push("/login?signup=success")
    } catch (error) {
      console.error("Signup failed", error)
      setIsLoading(false)
      throw error // Re-throw
    }
  }

  const logout = () => {
    setUser(null)
    setToken(null)
    localStorage.removeItem("accessToken")
    delete axios.defaults.headers.common["Authorization"]
    router.push("/login")
    setIsLoading(false)
  }

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, signup, logout, fetchUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
