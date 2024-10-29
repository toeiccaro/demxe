# Run application
```

uvicorn app.main:app --reload
```

# Set up virtual env

```
virtualenv demxe_django_env
```

# Activate environment
```
source demxe_env/bin/activate
```

# Migration init db
```
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE vehicles (
    id SERIAL PRIMARY KEY,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    trackId VARCHAR(255) NOT NULL,
    direction VARCHAR(255),
    image_path VARCHAR(255)
);


```