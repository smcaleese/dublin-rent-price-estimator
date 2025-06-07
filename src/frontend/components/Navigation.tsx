"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { useEffect, useState, Fragment } from "react" // Added Fragment
import { Button } from "@/components/ui/button"
// Tooltip not used directly in Navigation after this change, but HealthIndicator might use it.
// import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip" 
import axios from "axios"
import { FaCheckCircle } from "react-icons/fa"
import { LuCircleUser } from "react-icons/lu"
import { useAuth } from "@/context/AuthContext" // Import useAuth
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { CircleUser, LogIn, LogOut, UserPlus, History } from "lucide-react"
import { Avatar } from "@/components/ui/avatar"

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

function UserMenu() {
  const { user, logout, isLoading } = useAuth()

  if (isLoading) {
    return <p className="text-sm text-gray-500">Loading...</p>
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className="relative h-10 w-10 rounded-full"
        >
          <LuCircleUser className="h-10 w-10" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-56" align="end" forceMount>
        {user ? (
          <>
            <DropdownMenuLabel className="font-normal">
              <div className="flex flex-col space-y-1">
                <p className="text-sm font-medium leading-none">My Account</p>
                <p className="text-xs leading-none text-muted-foreground">
                  {user.email}
                </p>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <Link href="/search-history">
              <DropdownMenuItem className="cursor-pointer">
                <History className="mr-2 h-4 w-4" />
                <span>Search History</span>
              </DropdownMenuItem>
            </Link>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={logout} className="cursor-pointer text-red-600">
              <LogOut className="mr-2 h-4 w-4" />
              <span>Log out</span>
            </DropdownMenuItem>
          </>
        ) : (
          <>
            <DropdownMenuLabel>Guest</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <Link href="/signup">
              <DropdownMenuItem className="cursor-pointer">
                <UserPlus className="mr-2 h-4 w-4" />
                <span>Sign Up</span>
              </DropdownMenuItem>
            </Link>
            <Link href="/login">
              <DropdownMenuItem className="cursor-pointer">
                <LogIn className="mr-2 h-4 w-4" />
                <span>Log In</span>
              </DropdownMenuItem>
            </Link>
          </>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

export default function Navigation() {
  const pathname = usePathname()

  return (
    <nav className="flex items-center justify-between w-full">
      <div className="flex items-center space-x-2 ml-auto">
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
        <UserMenu />
      </div>
    </nav>
  )
}
