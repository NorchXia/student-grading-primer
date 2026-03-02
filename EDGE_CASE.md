# Edge Case

## Case: No students in the database
When there are no students stored in the database, the `/stats` endpoint still returns valid JSON.
It returns:
{
  "count": 0,
  "average": 0,
  "min": 0,
  "max": 0
}
## Reason
Returning zero values instead of null ensures consistent API structure and simplifies frontend handling.

