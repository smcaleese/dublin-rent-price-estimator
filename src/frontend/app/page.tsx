"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Home, MapPin, Bed, Bath } from "lucide-react"

export default function RentPredictor() {
  const [bedrooms, setBedrooms] = useState("")
  const [bathrooms, setBathrooms] = useState("")
  const [propertyType, setPropertyType] = useState("")
  const [dublinArea, setDublinArea] = useState("")
  const [predictedPrice, setPredictedPrice] = useState<number | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const bedroomOptions = [
    { value: "1", label: "1 Bedroom" },
    { value: "2", label: "2 Bedrooms" },
    { value: "3", label: "3 Bedrooms" },
    { value: "4", label: "4 Bedrooms" },
    { value: "5", label: "5+ Bedrooms" },
  ]

  const bathroomOptions = [
    { value: "1", label: "1 Bathroom" },
    { value: "2", label: "2 Bathrooms" },
    { value: "3", label: "3 Bathrooms" },
    { value: "4", label: "4+ Bathrooms" },
  ]

  const propertyTypeOptions = [
    { value: "apartment", label: "Apartment" },
    { value: "house", label: "House" },
    { value: "studio", label: "Studio" },
    { value: "townhouse", label: "Townhouse" },
    { value: "duplex", label: "Duplex" },
  ]

  const dublinAreaOptions = [
    { value: "dublin-1", label: "Dublin 1 (City Centre)" },
    { value: "dublin-2", label: "Dublin 2 (Southside)" },
    { value: "dublin-3", label: "Dublin 3 (Northside)" },
    { value: "dublin-4", label: "Dublin 4 (Ballsbridge)" },
    { value: "dublin-6", label: "Dublin 6 (Rathmines)" },
    { value: "dublin-8", label: "Dublin 8 (Liberties)" },
    { value: "dublin-15", label: "Dublin 15 (Blanchardstown)" },
    { value: "dun-laoghaire", label: "Dún Laoghaire" },
    { value: "blackrock", label: "Blackrock" },
    { value: "howth", label: "Howth" },
    { value: "malahide", label: "Malahide" },
    { value: "swords", label: "Swords" },
  ]

  const simulatePrediction = (): number => {
    // Simulate API call with realistic Dublin rent prices
    const basePrice = 1200
    const bedroomMultiplier = Number.parseInt(bedrooms) * 400
    const bathroomMultiplier = Number.parseInt(bathrooms) * 200

    let areaMultiplier = 1
    switch (dublinArea) {
      case "dublin-1":
      case "dublin-2":
      case "dublin-4":
        areaMultiplier = 1.4
        break
      case "dublin-6":
      case "blackrock":
      case "dun-laoghaire":
        areaMultiplier = 1.2
        break
      case "howth":
      case "malahide":
        areaMultiplier = 1.1
        break
      default:
        areaMultiplier = 1
    }

    let typeMultiplier = 1
    switch (propertyType) {
      case "house":
        typeMultiplier = 1.3
        break
      case "townhouse":
        typeMultiplier = 1.2
        break
      case "duplex":
        typeMultiplier = 1.15
        break
      case "studio":
        typeMultiplier = 0.7
        break
      default:
        typeMultiplier = 1
    }

    const prediction = Math.round(
      (basePrice + bedroomMultiplier + bathroomMultiplier) * areaMultiplier * typeMultiplier,
    )
    return prediction
  }

  const handlePredict = async () => {
    if (!bedrooms || !bathrooms || !propertyType || !dublinArea) {
      return
    }

    setIsLoading(true)

    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 1500))

    const prediction = simulatePrediction()
    setPredictedPrice(prediction)
    setIsLoading(false)
  }

  const isFormValid = bedrooms && bathrooms && propertyType && dublinArea

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-100 to-gray-50 p-4">
      <div className="max-w-2xl mx-auto space-y-8">
        <div className="text-center space-y-2 mt-4">
          <h1 className="text-4xl font-bold text-gray-900">Dublin Rent Predictor</h1>
          <p className="text-gray-600">Get an estimated rental price for properties in Dublin</p>
        </div>

        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Home className="h-5 w-5" />
              Property Details
            </CardTitle>
            <CardDescription>Fill in the details below to get a rent prediction</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="bedrooms" className="flex items-center gap-2">
                  <Bed className="h-4 w-4" />
                  Number of Bedrooms
                </Label>
                <Select value={bedrooms} onValueChange={setBedrooms}>
                  <SelectTrigger id="bedrooms" className="w-full">
                    <SelectValue placeholder="Select bedrooms" />
                  </SelectTrigger>
                  <SelectContent>
                    {bedroomOptions.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="bathrooms" className="flex items-center gap-2">
                  <Bath className="h-4 w-4" />
                  Number of Bathrooms
                </Label>
                <Select value={bathrooms} onValueChange={setBathrooms}>
                  <SelectTrigger id="bathrooms" className="w-full">
                    <SelectValue placeholder="Select bathrooms" />
                  </SelectTrigger>
                  <SelectContent>
                    {bathroomOptions.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="property-type" className="flex items-center gap-2">
                  <Home className="h-4 w-4" />
                  Property Type
                </Label>
                <Select value={propertyType} onValueChange={setPropertyType}>
                  <SelectTrigger id="property-type" className="w-full">
                    <SelectValue placeholder="Select property type" />
                  </SelectTrigger>
                  <SelectContent>
                    {propertyTypeOptions.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="dublin-area" className="flex items-center gap-2">
                  <MapPin className="h-4 w-4" />
                  Dublin Area
                </Label>
                <Select value={dublinArea} onValueChange={setDublinArea}>
                  <SelectTrigger id="dublin-area" className="w-full">
                    <SelectValue placeholder="Select Dublin area" />
                  </SelectTrigger>
                  <SelectContent>
                    {dublinAreaOptions.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <Button
              onClick={handlePredict}
              disabled={!isFormValid || isLoading}
              className="w-full h-12 text-lg cursor-pointer"
              size="lg"
            >
              {isLoading ? "Predicting..." : "Predict Price"}
            </Button>
          </CardContent>
        </Card>

        {predictedPrice && (
          <Card className="shadow-lg border-green-200 bg-green-50">
            <CardHeader>
              <CardTitle className="text-green-800">Predicted Rent Price</CardTitle>
              <CardDescription className="text-green-600">Based on your property details</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center space-y-2">
                <div className="text-4xl font-bold text-green-800">€{predictedPrice.toLocaleString()}</div>
                <div className="text-green-600">per month</div>
                <div className="text-sm text-green-600 mt-4 p-4 bg-green-100 rounded-lg">
                  <strong>Property Summary:</strong> {bedroomOptions.find((b) => b.value === bedrooms)?.label},{" "}
                  {bathroomOptions.find((b) => b.value === bathrooms)?.label},{" "}
                  {propertyTypeOptions.find((p) => p.value === propertyType)?.label} in{" "}
                  {dublinAreaOptions.find((a) => a.value === dublinArea)?.label}
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
