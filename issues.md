### Issues

- skill profile needs to be adjusted, should return the confidence and skill scores for each track {{}} ? || PAUSED
- skill profile cards for styling (accent, icons) to be resolved
- log in button does not turn blue when hovering over
- google pro pic not rendering, may have something to do with <DropDown> styling
- adding a submission should update the skill profile for that track || PAUSED
- research moving the database from SQLAlchemy to PostgreSQL
- use isLoggedIn for mcq page
- system retains google log in (it remembers) but jwt resets?
- logged in, but accessing mcq page tells me to login -> forced to then login with Google
- after completing mcq, view progress takes you to 404
- POST requests FAIL: http://localhost:8000/ 401 (Unauthorized) -> LOG: Posted the answer
- keep getting logged out of the system after completing MCQs, google login is retained in the background, but JWT resets


# When all the above is complete -> move to Phase 4 (Docker & Microservices)
