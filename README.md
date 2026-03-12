# HBnB Technical Documentation
## Architecture and Design Specifications

---

## Table of Contents

1. [Introduction](#introduction)
2. [High-Level Architecture](#high-level-architecture)
3. [Business Logic Layer](#business-logic-layer)
4. [API Interaction Flow](#api-interaction-flow)
5. [Conclusion](#conclusion)

---

## 1. Introduction

### 1.1 Project Overview

HBnB (Holberton BnB) is a comprehensive property rental application that allows users to list, search, and review accommodations. The application follows modern software architecture principles to ensure scalability, maintainability, and clear separation of concerns.

### 1.2 Purpose of This Document

This technical document serves as the architectural blueprint for the HBnB project. It provides:

- **Visual representations** of the system architecture through UML diagrams
- **Detailed specifications** of business logic components and their relationships
- **Interaction flows** showing how different layers communicate during API operations
- **Design rationale** explaining key architectural decisions

This documentation will guide the development team through implementation phases and serve as a reference for understanding the system's structure and behavior.

### 1.3 Document Scope

The document covers three main aspects:

1. **High-Level Architecture**: The overall layered structure and facade pattern
2. **Business Logic Layer**: Detailed class design and entity relationships
3. **API Interaction Flow**: Sequence diagrams for core API operations

---

## 2. High-Level Architecture

### 2.1 Overview

The HBnB application follows a **three-layered architecture** pattern, which provides clear separation of concerns and improves maintainability. The architecture is organized into three distinct layers:

1. **Presentation Layer** - Handles user interactions and API endpoints
2. **Business Logic Layer** - Contains core business rules and entity models
3. **Persistence Layer** - Manages data storage and retrieval

### 2.2 Architectural Pattern: Facade Pattern

The application implements the **Facade Pattern** to provide a simplified interface between layers. The Facade acts as a single entry point that:

- **Simplifies complexity**: Hides the intricate details of the business logic from the presentation layer
- **Reduces coupling**: The API layer doesn't need to know about individual model classes
- **Centralizes control**: All business operations go through a single, well-defined interface

### 2.3 High-Level Package Diagram

<img width="1074" height="1520" alt="API-Driven_Review_Ecosystem-2026-02-16-105122" src="https://github.com/user-attachments/assets/2ba3c6ca-c82c-4f02-936b-f5cbc93bad8f" />


### 2.4 Layer Responsibilities

#### Presentation Layer
- **Responsibilities**: Handle HTTP requests/responses, input validation, authentication, error formatting
- **Components**: RESTful API endpoints, request handlers, response serializers
- **Communication**: Interacts only with the Facade, never directly with models

#### Business Logic Layer
- **Responsibilities**: Implement business rules, data validation, entity relationships, business operations
- **Components**: Entity models (User, Place, Review, Amenity), Facade interface
- **Communication**: Receives requests from Presentation, sends queries to Persistence

#### Persistence Layer
- **Responsibilities**: Data storage, retrieval, CRUD operations, query execution
- **Components**: Database, ORM, data access objects
- **Communication**: Responds to queries from Business Logic layer

### 2.5 Design Rationale

**Why Three Layers?**
- **Separation of Concerns**: Each layer has a single, well-defined responsibility
- **Testability**: Layers can be tested independently with mock interfaces
- **Flexibility**: Database or UI changes don't affect business logic
- **Team Collaboration**: Different teams can work on different layers simultaneously

**Why Facade Pattern?**
- **Simplifies API Development**: Frontend developers work with a single interface
- **Encapsulation**: Business logic complexity is hidden from the API layer
- **Easier Refactoring**: Internal model changes don't affect the API interface
- **Consistent Interface**: All operations follow the same pattern

---

## 3. Business Logic Layer

### 3.1 Overview

The Business Logic Layer contains the core entities of the HBnB application. These entities represent the fundamental concepts of the system and encapsulate business rules and relationships.

### 3.2 Core Entities

The system is built around four main entities:

1. **User**: Represents registered users who can list properties and write reviews
2. **Place**: Represents rental properties listed by users
3. **Review**: Represents user feedback and ratings for places
4. **Amenity**: Represents features and facilities available at places

### 3.3 Detailed Class Diagram

<img width="1983" height="1471" alt="mermaid-diagram-2026-02-11-162915" src="https://github.com/user-attachments/assets/b8997064-1e91-4e2d-b250-b83fa5edf167" />


### 3.4 Entity Specifications

#### User Entity

**Purpose**: Manages user accounts and authentication

**Attributes**:
- `id`: Unique identifier (UUID)
- `email`: User's email address (unique, required for login)
- `password`: Hashed password (stored securely, never in plain text)
- `first_name`: User's first name
- `last_name`: User's last name
- `created_at`: Account creation timestamp
- `updated_at`: Last profile update timestamp

**Methods**:
- `register()`: Create a new user account with validation
- `login()`: Authenticate user credentials
- `update_profile()`: Modify user information
- `delete_account()`: Remove user account and related data

**Business Rules**:
- Email must be unique across all users
- Password must meet security requirements (minimum length, complexity)
- Users must be authenticated to create places or reviews

#### Place Entity

**Purpose**: Represents rental properties in the system

**Attributes**:
- `id`: Unique identifier (UUID)
- `title`: Property name/title
- `description`: Detailed description of the property
- `price`: Nightly rental price (must be positive)
- `latitude`: Geographic coordinate for location
- `longitude`: Geographic coordinate for location
- `owner_id`: Reference to the User who owns this place
- `created_at`: Listing creation timestamp
- `updated_at`: Last modification timestamp

**Methods**:
- `create()`: Add a new property listing
- `update()`: Modify property details
- `delete()`: Remove property listing
- `get_details()`: Retrieve complete property information

**Business Rules**:
- Price must be greater than zero
- Only the owner can update or delete a place
- Location coordinates must be valid latitude/longitude values
- Title and description are required fields

#### Review Entity

**Purpose**: Stores user feedback and ratings for places

**Attributes**:
- `id`: Unique identifier (UUID)
- `place_id`: Reference to the reviewed Place
- `user_id`: Reference to the User who wrote the review
- `rating`: Numerical rating (1-5 stars)
- `comment`: Written review text
- `created_at`: Review submission timestamp

**Methods**:
- `submit_review()`: Create a new review
- `update_review()`: Modify existing review
- `delete_review()`: Remove a review

**Business Rules**:
- Rating must be between 1 and 5 (inclusive)
- A user can only review a place once (no duplicate reviews)
- Users cannot review their own places
- Only the review author can update or delete their review

#### Amenity Entity

**Purpose**: Represents features and facilities available at places

**Attributes**:
- `id`: Unique identifier (UUID)
- `name`: Amenity name (e.g., "WiFi", "Pool", "Parking")
- `description`: Detailed description of the amenity

**Methods**:
- `create()`: Add a new amenity type
- `update()`: Modify amenity details
- `delete()`: Remove an amenity type

**Business Rules**:
- Amenity names should be unique
- Multiple places can offer the same amenity
- A place can have multiple amenities

### 3.5 Entity Relationships

#### User → Place (One-to-Many)
- **Relationship**: "owns"
- **Cardinality**: One user can own zero or many places
- **Implementation**: `owner_id` foreign key in Place table
- **Business Rule**: When a user is deleted, their places can either be deleted (cascade) or transferred to another user

#### User → Review (One-to-Many)
- **Relationship**: "writes"
- **Cardinality**: One user can write zero or many reviews
- **Implementation**: `user_id` foreign key in Review table
- **Business Rule**: When a user is deleted, their reviews should be deleted (cascade)

#### Place → Review (One-to-Many)
- **Relationship**: "has"
- **Cardinality**: One place can have zero or many reviews
- **Implementation**: `place_id` foreign key in Review table
- **Business Rule**: When a place is deleted, all its reviews should be deleted (cascade)

#### Place ↔ Amenity (Many-to-Many)
- **Relationship**: "offers"
- **Cardinality**: A place can have multiple amenities, and an amenity can belong to multiple places
- **Implementation**: Junction table `place_amenities` with `place_id` and `amenity_id`
- **Business Rule**: Removing an amenity type doesn't delete places; removing a place doesn't delete amenity types

### 3.6 Design Rationale

**Entity-Centric Design**
- Each entity represents a clear business concept
- Entities are independent and reusable
- Changes to one entity have minimal impact on others

**Relationship Design**
- Foreign keys ensure referential integrity
- Cascade delete operations maintain data consistency
- Many-to-many relationships use junction tables to avoid data duplication

**Attribute Selection**
- All entities have unique identifiers (UUID) for security and scalability
- Timestamps track creation and modification for audit purposes
- Required fields enforce data quality at the model level

---

## 4. API Interaction Flow

### 4.1 Overview

This section demonstrates how the three layers interact to handle specific API requests. Each sequence diagram shows the step-by-step flow of data and control through the system.

### 4.2 User Registration Flow

#### Description
When a new user registers, the system validates the email format, checks for duplicates, securely hashes the password, and stores the user data in the database.

#### Key Steps
1. Client sends registration data (email, password, name)
2. API validates request format
3. Business logic validates email format and uniqueness
4. Password is hashed for security
5. User data is persisted in the database
6. Success response returned with user ID

#### Error Handling
- **400 Bad Request**: Invalid JSON format, invalid email format
- **409 Conflict**: Email already registered
- **500 Internal Server Error**: Database save failure

#### Sequence Diagram

<img width="1983" height="1360" alt="mermaid-diagram-2026-02-12-123402" src="https://github.com/user-attachments/assets/c85b56d3-39ef-469f-8c67-b0d80b353a7d" />


#### Design Notes
- **Security**: Password is hashed before storage (never stored in plain text)
- **Validation**: Email format checked before database query to reduce load
- **Atomicity**: User creation is a single transaction to prevent partial records
- **Response**: Success response excludes password for security

---

### 4.3 Place Creation Flow

#### Description
An authenticated user creates a new property listing. The system verifies the user's identity, validates the place data, and stores the listing in the database.

#### Key Steps
1. Client sends place data with authentication token
2. API authenticates the user token
3. Business logic validates required fields and price
4. System verifies the user exists
5. Place data is persisted with generated ID
6. Success response returned with place details

#### Error Handling
- **401 Unauthorized**: Invalid or missing authentication token
- **400 Bad Request**: Missing required fields, invalid price value
- **404 Not Found**: User does not exist
- **500 Internal Server Error**: Database save failure

#### Sequence Diagram

<img width="1983" height="1360" alt="mermaid-diagram-2026-02-12-123434" src="https://github.com/user-attachments/assets/5d28e76c-468e-4ab4-8786-aa5d0a321b8a" />


#### Design Notes
- **Authentication**: Token validated before any business logic executes
- **Validation Order**: Field presence checked before value validation for efficiency
- **Referential Integrity**: User existence verified before linking place to user
- **Ownership**: Place automatically linked to authenticated user

---

### 4.4 Review Submission Flow

#### Description
A user submits a review for a place they visited. The system validates the rating, checks for duplicate reviews, stores the review, and updates the place's average rating.

#### Key Steps
1. Client sends review data with authentication
2. API authenticates the user
3. Business logic validates rating value (1-5)
4. System verifies place exists
5. System verifies user exists
6. System checks for duplicate review
7. Review is saved to database
8. Place's average rating is updated
9. Success response returned

#### Error Handling
- **401 Unauthorized**: Invalid or missing authentication token
- **400 Bad Request**: Invalid rating value (must be 1-5)
- **404 Not Found**: Place or user does not exist
- **409 Conflict**: User has already reviewed this place
- **500 Internal Server Error**: Database save failure

#### Sequence Diagram

<img width="1983" height="1360" alt="mermaid-diagram-2026-02-12-123446" src="https://github.com/user-attachments/assets/56c308bd-feee-450f-b9d2-b86ae6e101e6" />


#### Design Notes
- **Duplicate Prevention**: System enforces one review per user per place
- **Rating Validation**: Range checked (1-5) to ensure data quality
- **Atomic Update**: Review creation and rating update happen in a transaction
- **Business Rule**: Users cannot review their own places (enforced in business logic)

---

### 4.5 Fetching Places Flow

#### Description
A user requests a list of places based on search criteria such as location and price range. The system queries the database with filters and returns matching results.

#### Key Steps
1. Client sends GET request with query parameters
2. API parses query parameters
3. Business logic validates filter parameters
4. Query criteria is built from filters
5. Database is queried with criteria
6. Results are sorted by relevance
7. Place data is formatted
8. Response returned with array of places

#### Error Handling
- **400 Bad Request**: Invalid query format, invalid price range
- **500 Internal Server Error**: Database query error
- **200 OK**: Empty array if no results match criteria

#### Sequence Diagram

<img width="1983" height="1360" alt="mermaid-diagram-2026-02-12-123506" src="https://github.com/user-attachments/assets/86ee567c-1d60-4649-b23c-6e418b7f55fa" />


#### Design Notes
- **Optional Filters**: All query parameters are optional; no filters returns all places
- **Query Building**: Dynamic query construction based on provided filters
- **Performance**: Pagination should be implemented for large result sets
- **Sorting**: Results sorted by relevance or date (configurable)
- **Empty Results**: Returns 200 OK with empty array (not 404) when no matches found

---

### 4.6 Common Patterns Across All Flows

#### Authentication Pattern
All write operations (POST, PUT, DELETE) require authentication:
1. Token passed in Authorization header
2. Token validated at API layer before business logic
3. Invalid tokens result in 401 Unauthorized response

#### Validation Pattern
Validation occurs in two stages:
1. **API Layer**: Format validation (JSON structure, required parameters)
2. **Business Logic Layer**: Business rules validation (value ranges, relationships)

#### Error Response Pattern
All errors follow consistent format:
```json
{
  "error": {
    "code": 400,
    "message": "Invalid email format",
    "details": "Email must be a valid email address"
  }
}
```

#### Transaction Pattern
Operations that modify multiple entities use database transactions:
- Review submission updates both Review and Place (average rating)
- User deletion cascades to Places and Reviews
- Rollback occurs if any step fails

---

## 5. Conclusion

### 5.1 Architecture Summary

The HBnB application is built on a solid architectural foundation that emphasizes:

- **Separation of Concerns**: Three distinct layers with clear responsibilities
- **Maintainability**: Well-defined interfaces and the Facade pattern reduce coupling
- **Scalability**: Layered architecture allows horizontal scaling of individual layers
- **Testability**: Each layer can be tested independently with mock dependencies

### 5.2 Key Design Decisions

1. **Three-Layered Architecture**: Provides flexibility to change implementation details without affecting other layers
2. **Facade Pattern**: Simplifies the interface between Presentation and Business Logic layers
3. **Entity-Centric Design**: Core business concepts are modeled as independent entities
4. **RESTful API**: Standard HTTP methods and status codes for predictable behavior
5. **UUID Identifiers**: Ensures uniqueness and security for all entities

### 5.3 Implementation Guidelines

When implementing the HBnB application, development teams should:

1. **Follow the Layer Boundaries**: Never bypass the Facade to access models directly
2. **Respect Entity Relationships**: Maintain referential integrity through proper foreign keys
3. **Implement Error Handling**: Return appropriate HTTP status codes for all error cases
4. **Validate at Multiple Levels**: API layer for format, Business layer for rules
5. **Use Transactions**: Ensure data consistency for multi-entity operations
6. **Test Each Layer**: Write unit tests for models, integration tests for API endpoints

### 5.4 Future Considerations

As the application evolves, consider:

- **Caching Layer**: Add Redis for frequently accessed data (place listings, user profiles)
- **Message Queue**: Implement asynchronous processing for email notifications and analytics
- **API Versioning**: Support multiple API versions as features evolve
- **Rate Limiting**: Protect API endpoints from abuse
- **Search Optimization**: Implement full-text search for place descriptions
- **Geographic Search**: Use spatial databases for location-based queries

### 5.5 Documentation Maintenance

This technical document should be treated as a living document:

- Update diagrams when architecture changes
- Document new API endpoints as they are added
- Revise design rationale when requirements change
- Keep error codes and responses in sync with implementation

---

## Appendix

### A. Glossary

- **API**: Application Programming Interface - the set of endpoints that clients use to interact with the application
- **Facade Pattern**: A design pattern that provides a simplified interface to a complex subsystem
- **UUID**: Universally Unique Identifier - a 128-bit identifier that is unique across space and time
- **REST**: Representational State Transfer - an architectural style for designing networked applications
- **ORM**: Object-Relational Mapping - a technique for converting data between incompatible type systems
- **CRUD**: Create, Read, Update, Delete - the four basic operations on persistent storage

### B. HTTP Status Codes Used

- **200 OK**: Request succeeded
- **201 Created**: Resource successfully created
- **400 Bad Request**: Invalid request format or parameters
- **401 Unauthorized**: Authentication required or failed
- **404 Not Found**: Resource does not exist
- **409 Conflict**: Request conflicts with current state (e.g., duplicate)
- **500 Internal Server Error**: Server-side error occurred

### C. References

- RESTful API Design Best Practices
- UML Sequence Diagram Tutorial
- Design Patterns: Facade Pattern
- Three-Tier Architecture Patterns

---

**Document Version**: 1.0  
**Last Updated**: February 2026  
**Project**: HBnB (Holberton BnB)  
**Repository**: holbertonschool-hbnb
