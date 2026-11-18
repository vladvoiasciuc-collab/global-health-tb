# Lab 3 Results – Layered Architecture

## Task 3.1 – Screenshot of the running application

_Add screenshots here:_
- Main page with filters
- Filtered by region + sex
- Pagination working

## Task 3.2 – Region filter through all layers

The region filter was added by extending the existing `ObservationCriteria` and flowing it through every layer:

1. **Domain** (`app/domain.py`)  
   Added `region: str | None = None` to `ObservationCriteria`.

2. **Repository** (`app/repositories/observation_repository.py`)  
   In `_conditions()` we added:
   ```python
   if criteria.region is not None:
       conditions.append(Country.region == criteria.region)
   ```

3. **Service** (`app/services/observation_service.py`)  
   No change needed — it only passes the criteria object down to the repository.

4. **Controller** (`app/controllers/observation_controller.py`)  
   The query parameter `region` is converted with `blank_to_none` and put into `ObservationCriteria`.

5. **Template** (`app/templates/observations.html`)  
   Added a `<select name="region">` that lists the available regions from `FilterOptions`.

This shows the dependency rule in action: the controller never talks to the database, the service never builds SQL, and the repository never knows about HTTP.

## Task 3.3 – Sex filter

The sex filter follows the exact same pattern (already implemented).  
`Sex` enum lives in the domain layer and is used by repository, controller and template.

## Task 3.4 – Tests

- `tests/test_architecture.py` enforces the dependency rule.
- Additional unit tests can be added for the service and repository (mocked).
