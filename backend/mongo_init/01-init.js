// MongoDB initialization script
// This script will be executed when the MongoDB container starts

// Switch to the application database
db = db.getSiblingDB('mydb');

// Create the swift_codes collection with validation
db.createCollection("swift_codes", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["swiftCode", "address", "countryISO2", "countryName", "isHeadquarter"],
      properties: {
        swiftCode: {
          bsonType: "string",
          minLength: 8,
          maxLength: 11,
          pattern: "^[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?$",
          description: "SWIFT/BIC code - must be 8 or 11 characters, following SWIFT format"
        },
        address: {
          bsonType: "string",
          minLength: 1,
          maxLength: 255,
          description: "Physical address of the bank/branch"
        },
        countryISO2: {
          bsonType: "string",
          minLength: 2,
          maxLength: 2,
          pattern: "^[A-Z]{2}$",
          description: "Two-letter ISO country code"
        },
        countryName: {
          bsonType: "string",
          minLength: 1,
          maxLength: 100,
          description: "Full name of the country"
        },
        isHeadquarter: {
          bsonType: "bool",
          description: "Flag indicating if this is a headquarter location"
        }
      }
    }
  }
});

// Create unique index on swiftCode
db.swift_codes.createIndex({ "swiftCode": 1 }, { unique: true });

// Create additional indexes for common queries
db.swift_codes.createIndex({ "countryISO2": 1 });
db.swift_codes.createIndex({ "isHeadquarter": 1 });
db.swift_codes.createIndex({ "countryISO2": 1, "isHeadquarter": 1 });

// Insert sample data
db.swift_codes.insertMany([
  {
    swiftCode: "DEUTDEFF",
    address: "Taunusanlage 12, 60325 Frankfurt am Main",
    countryISO2: "DE",
    countryName: "Germany",
    isHeadquarter: false
  },
  {
    swiftCode: "DEUTDEFFXXX",
    address: "Taunusanlage 12, 60325 Frankfurt am Main",
    countryISO2: "DE",
    countryName: "Germany",
    isHeadquarter: true
  },
  {
    swiftCode: "CHASUS33",
    address: "270 Park Avenue, New York",
    countryISO2: "US",
    countryName: "United States",
    isHeadquarter: false
  },
  {
    swiftCode: "CHASJPJT",
    address: "Tokyo Building, 2-7-3, Marunouchi, Chiyoda-ku",
    countryISO2: "JP",
    countryName: "Japan",
    isHeadquarter: false
  }
]);

print("MongoDB initialization completed. Collection 'swift_codes' created with sample data.");