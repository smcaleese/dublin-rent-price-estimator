"use client"

import { useState } from "react"
import axios from "axios"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import { Home, MapPin, Bed, Bath, Users } from "lucide-react"

interface SubmittedDetails {
  bedrooms?: string | null
  bathrooms?: string | null
  propertyType: string
  dublinArea: string
  isShared: boolean
  roomType?: string | null
}

export default function PredictionPage() {
  const [activeFormType, setActiveFormType] = useState<'property' | 'sharing'>('property')
  const [bedrooms, setBedrooms] = useState("")
  const [bathrooms, setBathrooms] = useState("")
  const [propertyType, setPropertyType] = useState("")
  const [dublinArea, setDublinArea] = useState("")
  const [roomType, setRoomType] = useState("")
  const [predictedPrice, setPredictedPrice] = useState<number | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [submittedDetails, setSubmittedDetails] = useState<SubmittedDetails | null>(null)


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
    { value: "dublin-5", label: "Dublin 5 (Raheny)" },
    { value: "dublin-6", label: "Dublin 6 (Rathmines)" },
    { value: "dublin-7", label: "Dublin 7 (Phibsborough)" },
    { value: "dublin-8", label: "Dublin 8 (Liberties)" },
    { value: "dublin-9", label: "Dublin 9 (Drumcondra)" },
    { value: "dublin-10", label: "Dublin 10 (Ballyfermot)" },
    { value: "dublin-11", label: "Dublin 11 (Finglas)" },
    { value: "dublin-12", label: "Dublin 12 (Drimnagh)" },
    { value: "dublin-13", label: "Dublin 13 (Howth)" },
    { value: "dublin-14", label: "Dublin 14 (Dundrum)" },
    { value: "dublin-15", label: "Dublin 15 (Blanchardstown)" },
    { value: "dublin-16", label: "Dublin 16 (Ballinteer)" },
    { value: "dublin-17", label: "Dublin 17 (Coolock)" },
    { value: "dublin-18", label: "Dublin 18 (Foxrock)" },
    { value: "dublin-20", label: "Dublin 20 (Palmerstown)" },
    { value: "dublin-22", label: "Dublin 22 (Clondalkin)" },
    { value: "dublin-24", label: "Dublin 24 (Tallaght)" },
  ]

  const roomTypeOptions = [
    { value: "single", label: "Single Room" },
    { value: "double", label: "Double Room" },
    { value: "twin", label: "Twin Room" },
    { value: "shared", label: "Shared Room" },
  ]

  const handlePredict = async () => {
    setIsLoading(true)
    setPredictedPrice(null)
    setSubmittedDetails(null)

    let payload: any = {}
    let currentSubmittedDetails: SubmittedDetails | null = null

    if (activeFormType === "property") {
      if (!bedrooms || !bathrooms || !propertyType || !dublinArea) {
        setIsLoading(false)
        return
      }
      payload = {
        bedrooms,
        bathrooms,
        propertyType,
        dublinArea,
        isShared: false,
        roomType: null,
      }
      currentSubmittedDetails = { bedrooms, bathrooms, propertyType, dublinArea, isShared: false, roomType: null }
    } else { // activeFormType === "sharing"
      if (!propertyType || !dublinArea || !roomType) {
        setIsLoading(false)
        return
      }
      payload = {
        propertyType,
        dublinArea,
        isShared: true,
        roomType,
      }
      currentSubmittedDetails = { propertyType, dublinArea, roomType, isShared: true }
    }

    try {
      const response = await axios.post("http://localhost:8000/predict", payload)
      setPredictedPrice(response.data.predictedPrice)
      setSubmittedDetails(currentSubmittedDetails)
    } catch (error) {
      console.error("Network or other error:", error)
      // TODO: Display error to user
    } finally {
      setIsLoading(false)
    }
  }

  const isFormValid = () => {
    if (activeFormType === "property") {
      return !!(bedrooms && bathrooms && propertyType && dublinArea)
    } else { // activeFormType === "sharing"
      return !!(propertyType && dublinArea && roomType)
    }
  }

  const handleTabChange = (value: string) => {
    setActiveFormType(value as 'property' | 'sharing')
    // Optionally reset form fields when tab changes to avoid confusion
    setBedrooms("")
    setBathrooms("")
    setPropertyType("")
    setDublinArea("")
    setRoomType("")
    setPredictedPrice(null) // Clear prediction when tab changes
    setSubmittedDetails(null)
  }


  const renderPropertyForm = () => (
    <div className="space-y-6">
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
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-2">
          <Label htmlFor="property-type-prop" className="flex items-center gap-2">
            <Home className="h-4 w-4" />
            Property Type
          </Label>
          <Select value={propertyType} onValueChange={setPropertyType}>
            <SelectTrigger id="property-type-prop" className="w-full">
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
          <Label htmlFor="dublin-area-prop" className="flex items-center gap-2">
            <MapPin className="h-4 w-4" />
            Dublin Area
          </Label>
          <Select value={dublinArea} onValueChange={setDublinArea}>
            <SelectTrigger id="dublin-area-prop" className="w-full">
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
    </div>
  )

  const renderSharedRoomForm = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-2">
          <Label htmlFor="property-type-shared" className="flex items-center gap-2">
            <Home className="h-4 w-4" />
            Property Type
          </Label>
          <Select value={propertyType} onValueChange={setPropertyType}>
            <SelectTrigger id="property-type-shared" className="w-full">
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
          <Label htmlFor="dublin-area-shared" className="flex items-center gap-2">
            <MapPin className="h-4 w-4" />
            Dublin Area
          </Label>
          <Select value={dublinArea} onValueChange={setDublinArea}>
            <SelectTrigger id="dublin-area-shared" className="w-full">
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
      <div className="space-y-2">
        <Label htmlFor="room-type" className="flex items-center gap-2">
          <Users className="h-4 w-4" />
          Room Type
        </Label>
        <Select value={roomType} onValueChange={setRoomType}>
          <SelectTrigger id="room-type" className="w-full">
            <SelectValue placeholder="Select room type" />
          </SelectTrigger>
          <SelectContent>
            {roomTypeOptions.map((option) => (
              <SelectItem key={option.value} value={option.value}>
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    </div>
  )

  return (
    <div className="space-y-8 mt-8">
      <Card className="shadow-lg">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {activeFormType === 'property' ? <Home className="h-5 w-5" /> : <Users className="h-5 w-5" />}
            {activeFormType === 'property' ? "Property Details" : "Shared Room Details"}
          </CardTitle>
          <CardDescription>
            {activeFormType === 'property'
              ? "Fill in property details to predict rent for an entire property"
              : "Fill in details to predict rent for a shared room/accommodation"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs value={activeFormType} onValueChange={handleTabChange} className="w-full">
            <TabsList className="grid w-full grid-cols-2 mb-6">
              <TabsTrigger value="property">Entire Property</TabsTrigger>
              <TabsTrigger value="sharing">Shared Room</TabsTrigger>
            </TabsList>
            <TabsContent value="property" className="space-y-6">
              {renderPropertyForm()}
            </TabsContent>
            <TabsContent value="sharing" className="space-y-6">
              {renderSharedRoomForm()}
            </TabsContent>
          </Tabs>

          <Button
            onClick={handlePredict}
            disabled={!isFormValid() || isLoading}
            className="w-full h-12 text-lg cursor-pointer mt-6"
            size="lg"
          >
            {isLoading ? "Predicting..." : "Predict Price"}
          </Button>
        </CardContent>
      </Card>

      {predictedPrice && submittedDetails && (
        <Card className="shadow-lg border-green-200 bg-green-50">
          <CardHeader>
            <CardTitle className="text-green-800">Predicted Rent Price</CardTitle>
            <CardDescription className="text-green-600">
              Based on {submittedDetails.isShared ? "shared room" : "property"} details
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center space-y-2">
              <div className="text-4xl font-bold text-green-800">€{predictedPrice.toLocaleString()}</div>
              <div className="text-green-600">per month</div>
              <div className="text-sm text-green-600 mt-4 p-4 bg-green-100 rounded-lg">
                <strong>Summary:</strong>
                {!submittedDetails.isShared && submittedDetails.bedrooms && (
                  <> {bedroomOptions.find((b) => b.value === submittedDetails.bedrooms)?.label},</>
                )}
                {!submittedDetails.isShared && submittedDetails.bathrooms && (
                  <> {bathroomOptions.find((b) => b.value === submittedDetails.bathrooms)?.label},</>
                )}
                <> {propertyTypeOptions.find((p) => p.value === submittedDetails.propertyType)?.label}</>
                <> in {dublinAreaOptions.find((a) => a.value === submittedDetails.dublinArea)?.label}</>
                {submittedDetails.isShared && submittedDetails.roomType && (
                  <span>
                    {" "}- {roomTypeOptions.find((r) => r.value === submittedDetails.roomType)?.label} (Shared)
                  </span>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
