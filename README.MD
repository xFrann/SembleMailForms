# SembleMailForms

Simple backend with rest api and smtplib used to 
send emails to the correct recipients based on what website it has been sent from.

Flask api + built in python smptlib

# Configuration

Download the release and first change the configuration file found in the ```configs``` directory

Here you will find ```config.yml``` which contains SMTP Server and API binding configuration

The configuration file is pretty self-explanatory, example config below:

```yaml
# API Binding configuration
# This can sit behind a reverse proxy
host: "0.0.0.0"
port: 1025

# Endpoint configuration
email_ratelimit: "3/minutes" # This translates to 3 requests per minute from the same IP


# Email configuration
# Only supports starttls (port 587)
mail_host: "smtp.hostinger.com"
mail_port: 587 # Don't change, even if provider does not use tls, the protocol will handle it
mail_username: "contact@sembleit.ro"
```

Please note starttls is forced, so it's necessary to use port 587, if the provider does not support tls 
that is not a problem as it will use whatever type of connection is available.

The ```recipient_map.yml``` contains an ID - Array map which basically
maps and unique identifier to a list of recipients, when a post request is received,
the server will look in the post request body for this unique identifier, if not present or incorrect,
the request will fail and no email will be sent. If a valid unique id is found, the email will be sent
to the mapped recipients

The UUID's are generated using this [UUID Generator](https://uuidgenerator.net)

This method is used in order not to expose all the recipients emails to the frontend, see example
of how this works below

```yaml
# Example UUID - Recipients map (recipient_map.yml)
b21d9028-d98b-44fb-a9b1-b441b94cad58: ["example@frann.dev", "example2@frann.dev"]
```

See below example for a post request body example, this will
email the recipients mapped to the UUID above


```json
{
    "name": "Your Name",
    "message": "Your Email Body here",
    "UUID": "b21d9028-d98b-44fb-a9b1-b441b94cad58"
}
```

# Frontend implementation
Simply perform a http request with the data you want, see a below JS example

```javascript
function sembleEmailRequest() {

    let form_data = {
        "name": "Your Name",
        "message": "Your Email Body here",
        "UUID": "b21d9028-d98b-44fb-a9b1-b441b94cad58"
    }

    fetch("https://email.sembleit.ro/", {
        method: 'POST',
        body: form_data,
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    }).then((response) => {
        console.log(response.json())
        return response.json();
    }).catch((error) => {
        console.log(error)
    });
}
```

# Feel free to create your own docker-compose.yml, take below example:
```
semble_email:
  container_name: semble-email-container
    build: .
    restart: unless-stopped
    ports:
      - "127.0.0.1:1025:1025"
    volumes:
      - ./semble_email/configs:/home/semble_email/configs
    environment:
      - SEMBLE_MAIL_PASSWORD=YOUREMAILPASSWORDHERE
```
Note that the email password will only work trough env variable when docker is used, manually inserting password at startup is not supported currently.
In the directory then run `sudo docker compose up -d`


# Usage

Download the latest release from github, open a command prompt 
in the directory and run using ```py main.py```<br/>
If the config file is valid, it will try to connect to the SMTP server and prompt for the account's password<br/>
If the password is correct the API will start listening and HTTP requests can be made.
