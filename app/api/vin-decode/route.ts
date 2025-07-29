import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { vin } = await request.json();

    // Validate VIN format
    if (!vin || typeof vin !== 'string') {
      return NextResponse.json(
        { error: 'VIN is required' },
        { status: 400 }
      );
    }

    const cleanVin = vin.replace(/[^A-HJ-NPR-Z0-9]/gi, '').toUpperCase();
    
    if (cleanVin.length !== 17) {
      return NextResponse.json(
        { error: 'VIN must be exactly 17 characters' },
        { status: 400 }
      );
    }

    // For demo purposes, we'll use the free NHTSA API
    // In production, you might want to use a more comprehensive service
    const nhtsa_url = `https://vpic.nhtsa.dot.gov/api/vehicles/decodevin/${cleanVin}?format=json`;
    
    try {
      const response = await fetch(nhtsa_url);
      const data = await response.json();
      
      if (!data.Results) {
        throw new Error('Invalid response from NHTSA API');
      }

      // Extract relevant vehicle information
      const results = data.Results;
      const vehicleInfo = {
        vin: cleanVin,
        make: getValueByVariable(results, 'Make') || '',
        model: getValueByVariable(results, 'Model') || '',
        year: getValueByVariable(results, 'Model Year') || '',
        trim: getValueByVariable(results, 'Trim') || '',
        engine: getValueByVariable(results, 'Engine Number of Cylinders') || '',
        transmission: getValueByVariable(results, 'Transmission Style') || '',
        bodyClass: getValueByVariable(results, 'Body Class') || '',
        fuelType: getValueByVariable(results, 'Fuel Type - Primary') || '',
        manufacturer: getValueByVariable(results, 'Manufacturer Name') || '',
        plantCountry: getValueByVariable(results, 'Plant Country') || '',
        vehicleType: getValueByVariable(results, 'Vehicle Type') || '',
        driveType: getValueByVariable(results, 'Drive Type') || '',
      };

      // Add estimated values based on year and make (mock data for demo)
      const currentYear = new Date().getFullYear();
      const vehicleAge = currentYear - parseInt(vehicleInfo.year);
      
      const estimatedValues = {
        tradeInValue: calculateTradeInValue(vehicleInfo.make, vehicleInfo.year, vehicleAge),
        retailValue: calculateRetailValue(vehicleInfo.make, vehicleInfo.year, vehicleAge),
        marketTrend: getMarketTrend(vehicleInfo.make),
      };

      return NextResponse.json({
        success: true,
        vehicle: {
          ...vehicleInfo,
          ...estimatedValues,
          decodedAt: new Date().toISOString(),
        }
      });

    } catch (apiError) {
      console.error('NHTSA API Error:', apiError);
      
      // Fallback to mock data for development/demo
      const mockVehicleInfo = generateMockVehicleInfo(cleanVin);
      
      return NextResponse.json({
        success: true,
        vehicle: mockVehicleInfo,
        note: "Using demo data - NHTSA API unavailable"
      });
    }

  } catch (error) {
    console.error('VIN Decode Error:', error);
    return NextResponse.json(
      { error: 'Failed to decode VIN' },
      { status: 500 }
    );
  }
}

// Helper function to extract values from NHTSA API response
function getValueByVariable(results: any[], variableName: string): string {
  const result = results.find(item => item.Variable === variableName);
  return result?.Value || '';
}

// Mock calculation functions (replace with real valuation APIs)
function calculateTradeInValue(make: string, year: string, age: number): string {
  const baseValues: { [key: string]: number } = {
    'TOYOTA': 25000,
    'HONDA': 23000,
    'FORD': 20000,
    'CHEVROLET': 18000,
    'NISSAN': 19000,
    'BMW': 35000,
    'MERCEDES-BENZ': 40000,
    'LEXUS': 32000,
    'AUDI': 30000,
  };
  
  const baseValue = baseValues[make.toUpperCase()] || 15000;
  const depreciatedValue = Math.max(baseValue - (age * 2000), 3000);
  
  return `$${depreciatedValue.toLocaleString()}`;
}

function calculateRetailValue(make: string, year: string, age: number): string {
  const tradeValue = parseInt(calculateTradeInValue(make, year, age).replace(/[$,]/g, ''));
  const retailValue = Math.round(tradeValue * 1.25);
  
  return `$${retailValue.toLocaleString()}`;
}

function getMarketTrend(make: string): string {
  const trends = ['Rising', 'Stable', 'Declining'];
  const popularMakes = ['TOYOTA', 'HONDA', 'LEXUS'];
  
  if (popularMakes.includes(make.toUpperCase())) {
    return Math.random() > 0.3 ? 'Rising' : 'Stable';
  }
  
  return trends[Math.floor(Math.random() * trends.length)];
}

// Fallback mock data generator
function generateMockVehicleInfo(vin: string) {
  const makes = ['Toyota', 'Honda', 'Ford', 'Chevrolet', 'Nissan'];
  const models = ['Sedan', 'SUV', 'Truck', 'Hatchback', 'Coupe'];
  const years = ['2018', '2019', '2020', '2021', '2022', '2023'];
  
  const randomMake = makes[Math.floor(Math.random() * makes.length)];
  const randomModel = models[Math.floor(Math.random() * models.length)];
  const randomYear = years[Math.floor(Math.random() * years.length)];
  
  return {
    vin,
    make: randomMake,
    model: randomModel,
    year: randomYear,
    trim: 'Standard',
    engine: '4 Cylinder',
    transmission: 'Automatic',
    bodyClass: 'Sedan',
    fuelType: 'Gasoline',
    manufacturer: randomMake,
    plantCountry: 'USA',
    vehicleType: 'Passenger Car',
    driveType: 'FWD',
    tradeInValue: calculateTradeInValue(randomMake, randomYear, new Date().getFullYear() - parseInt(randomYear)),
    retailValue: calculateRetailValue(randomMake, randomYear, new Date().getFullYear() - parseInt(randomYear)),
    marketTrend: getMarketTrend(randomMake),
    decodedAt: new Date().toISOString(),
  };
}