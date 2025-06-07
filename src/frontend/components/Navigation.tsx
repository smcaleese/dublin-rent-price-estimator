"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { useEffect, useState, Fragment } from "react" // Added Fragment
import { Button } from "@/components/ui/button"
// Tooltip not used directly in Navigation after this change, but HealthIndicator might use it.
// import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip" 
import axios from "axios"
import { FaCheckCircle } from "react-icons/fa"
import { useAuth } from "@/context/AuthContext" // Import useAuth

interface HealthStatus {
  status: string
  property_model_trained: boolean
  shared_model_trained: boolean
  both_models_ready: boolean
}

function HealthIndicator() {
  const [healthStatus, setHealthStatus] = useState<HealthStatus | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await axios.get('http://localhost:8000/healthcheck')
        const data = response.data
        setHealthStatus(data)
      } catch (error) {
        console.error('Health check failed:', error)
        setHealthStatus({ 
          status: 'error', 
          property_model_trained: false, 
          shared_model_trained: false, 
          both_models_ready: false 
        })
      } finally {
        setIsLoading(false)
      }
    }

    // Check immediately
    checkHealth()

    // Check every 60 seconds
    const interval = setInterval(checkHealth, 60000)

    return () => clearInterval(interval)
  }, [])

  const isHealthy = healthStatus?.status === 'healthy'
  
  const indicatorText = isLoading 
    ? 'Checking...' 
    : isHealthy 
    ? 'System Online' 
    : 'System Issues'

  return (
    <div className="flex items-center space-x-2 mx-6">
      <FaCheckCircle className={`${isLoading ? 'text-yellow-500' : isHealthy ? 'text-green-500' : 'text-red-500'}`} size={16} />
      <span className={`text-sm text-gray-600 hidden sm:inline ${isLoading ? 'text-yellow-500' : isHealthy ? 'text-green-500' : 'text-red-500'} md:block`}>
        {indicatorText}
      </span>
    </div>
  )
}

export default function Navigation() {
  const pathname = usePathname()
  const { user, logout, isLoading } = useAuth()

  return (
    <nav className="flex items-center justify-between w-full">
      <div className="flex items-center space-x-2 ml-auto"> {/* Added items-center for vertical alignment */}
        <HealthIndicator />
        <Link href="/">
          <Button
            variant={pathname === "/" ? "default" : "ghost"}
            className={pathname === "/"
              ? "text-white bg-blue-600 hover:bg-blue-700 cursor-pointer"
              : "text-gray-700 hover:text-gray-900 cursor-pointer"
            }
          >
            Rent Predictor
          </Button>
        </Link>
        <Link href="/model-info">
          <Button
            variant={pathname === "/model-info" ? "default" : "ghost"}
            className={pathname === "/model-info"
              ? "text-white bg-blue-600 hover:bg-blue-700 cursor-pointer"
              : "text-gray-700 hover:text-gray-900 cursor-pointer"
            }
          >
            Model Info
          </Button>
        </Link>

        {isLoading ? (
          <p className="text-sm text-gray-500">Loading...</p>
        ) : user ? (
          <>
            <span className="text-sm text-gray-700 hidden sm:inline">Welcome, {user.email}</span>
            <Button
              variant="ghost"
              onClick={logout}
              className="text-red-600 hover:text-red-800 cursor-pointer"
            >
              Log Out
            </Button>
          </>
        ) : (
          <>
            <Link href="/signup">
              <Button
                variant={pathname === "/signup" ? "default" : "ghost"}
                className={pathname === "/signup"
                  ? "text-white bg-green-600 hover:bg-green-700 cursor-pointer"
                  : "text-gray-700 hover:text-gray-900 cursor-pointer"
                }
              >
                Sign Up
              </Button>
            </Link>
            <Link href="/login">
              <Button
                variant={pathname === "/login" ? "default" : "ghost"}
                className={pathname === "/login"
                  ? "text-white bg-indigo-600 hover:bg-indigo-700 cursor-pointer"
                  : "text-gray-700 hover:text-gray-900 cursor-pointer"
                }
              >
                Log In
              </Button>
            </Link>
          </>
        )}
      </div>
    </nav>
  )
}
