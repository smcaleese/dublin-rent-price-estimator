"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"
import axios from "axios"
import { FaCheckCircle } from "react-icons/fa"

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

  return (
    <nav className="flex items-center justify-between w-full">
      <div className="flex space-x-2 ml-auto">
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
      </div>
    </nav>
  )
}
