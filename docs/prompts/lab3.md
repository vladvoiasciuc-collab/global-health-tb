# Lab 3 – AI Prompts Used

## Architecture & structure

**Prompt:**  
"Create a layered architecture for a FastAPI + SQLAlchemy app that shows TB observations. Layers: domain, repositories, services, controllers, templates, dependencies. Controllers must not import SQLAlchemy. Services must not import FastAPI."

## Domain model

**Prompt:**  
"Define frozen dataclasses for ObservationCriteria and ObservationListItem. Include optional filters: country_iso3, indicator_code, region, year_from, year_to, sex. Sex should be an Enum with MLE, FML, BTSX."

## Repository

**Prompt:**  
"Write an ObservationRepository that takes a Session and implements find(), count(), list_countries(), list_indicators(), list_regions(). Use SQLAlchemy select and joins. No business logic."

## Service

**Prompt:**  
"Write an ObservationService that receives the repository and implements get_page() with pagination and get_filter_options(). No SQL, no HTTP."

## Controller & template

**Prompt:**  
"Create a FastAPI router that uses dependency injection for the service. Convert query parameters into ObservationCriteria and render observations.html with Jinja2. Include a region and sex dropdown."

## Tests

**Prompt:**  
"Write a test that parses all Python files in app/ and verifies that no layer imports from a higher layer (dependency rule)."
