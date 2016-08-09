# Register
> /register
> ## POST
> ```json
> {
>     "username" : "testuser",
>     "password" : "passwd",
>     "email" : "email@email.com"
> }
> ```
> ## Response OK
> ```json
> {
>   "message": "User created successfully.",
>   "user": {
>     "email": "email@email.com",
>     "id": 1,
>     "username": "testuser"
>   }
> }
> ```
> ## Response Conflict
> ```json
> {
>   "message": "Username  testuser already in use"
> }
> ```



# Auth
> /auth
> ## POST
> ```json
>
> {
> 	"username" : "testuser",
> 	"password" : "passwd"
> }
>
> ```
> ## Response OK
> ```json
> {
>   "access_token":  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZGVudGl0eSI6MSwiaWF0IjoxNDY5NzEwMjI1LCJuYmYiOj > E0Njk3MTAyMjUsImV4cCI6MTQ2OTcxMDUyNX0.xR21mf7SnGbw8h74N9GhCcEXirSVAcM_CDCIpmmiK2I"
> }
> ```
> ## Response Unauthorized
> ```json
> {
>   "description": "Invalid credentials",
>   "error": "Bad Request",
>   "status_code": 401
> }
> ```

# Devices
> /dev
> ##GET
> ###Headers
> Authorization : JWT *Access Token*
> ## Response
> ```json
> {
>   "data": [
>     {
>       "created_at": "2016-07-26T10:42:51.226222+00:00",
>       "id": 1,
>       "name": "testdev22",
>       "status": 0,
>       "topic": "/test/topic",
>       "updated_at": "2016-07-26T10:42:51.226222+00:00",
>       "user": {
>         "email": "testuser@testhost.com",
>         "id": 1,
>         "username": "testuser"
>       }
>     },
>     {
>       "created_at": "2016-07-26T10:45:46.002009+00:00",
>       "id": 2,
>       "name": "testuserdev22",
>       "status": 0,
>       "topic": "passwd/topic",
>       "updated_at": "2016-07-26T10:45:46.002009+00:00",
>       "user": {
>         "email": "testuser@testhost.com",
>         "id": 1,
>         "username": "testuser"
>       }
>     }
>   ],
>   "message": "All devices of testuser"
> }
> ```

> /dev/:id:
> ## GET
> ### Headers
> Authorization : JWT *Access Token*
> ## Response
> ```json
> {
>   "data": {
>     "created_at": "2016-07-26T10:42:51.226222+00:00",
>     "id": 1,
>     "name": "testdev22",
>     "status": 0,
>     "topic": "/test/topic",
>     "updated_at": "2016-07-26T10:42:51.226222+00:00",
>     "user": {
>       "email": "testuser@testhost.com",
>       "id": 1,
>       "username": "testuser"
>     }
>   },
>   "message": "Device 1"
> }
> ```
> ## POST
> ### Headers
> Authorization : JWT *Access Token*
> ```json
> {
>     "name" : "device name",
>     "topic" : "device/topic"
> }
> ```
> ## Response
> ```json
> {
>   "data": {
>     "created_at": "2016-07-28T13:08:23.362662",
>     "id": 16,
>     "name": "device name",
>     "topic": "device/topic",
>     "updated_at": "2016-07-28T13:08:23.362662",
>     "user": {
>       "email": "testuser@testhost.com",
>       "id": 1,
>       "username": "testuser"
>     }
>   },
>   "message": "Device registered successfuly"
> }
> ```

# PasswordReset
> /passreset
> ## POST
> ```json
> {
>     "email" : "<email>"
> }
> ```
