"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Button } from "@/components/ui/button"

export default function Navigation() {
  const pathname = usePathname()

  return (
    <nav className="flex space-x-2">
      <Link href="/">
        <Button 
          variant={pathname === "/" ? "default" : "ghost"} 
          className={pathname === "/" 
            ? "text-white bg-blue-600 hover:bg-blue-700" 
            : "text-gray-700 hover:text-gray-900"
          }
        >
          Rent Predictor
        </Button>
      </Link>
      <Link href="/model-info">
        <Button 
          variant={pathname === "/model-info" ? "default" : "ghost"} 
          className={pathname === "/model-info" 
            ? "text-white bg-blue-600 hover:bg-blue-700" 
            : "text-gray-700 hover:text-gray-900"
          }
        >
          Model Info
        </Button>
      </Link>
    </nav>
  )
}
