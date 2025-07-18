# utlectives instructions

## Server

1. Git clone repository

```python
git clone --branch filter-rewrite --single-branch https://github.com/charmandercodes/utlectives.git . && rm -rf .git
```

1. Create virtual environment

```python
python3 -m venv venv
```
2. Activate virtual environment

```python
source venv/bin/activate
```

3. upgrade pip

```python
pip install --upgrade pip 
```

4. Install requirements.txt

```python
pip install -r requirements.txt 
```

5. migrate the database

```python
python manage.py migrate
```

6. Create admin user

```python
python manage.py createsuperuser
```

7. Run server

```python
python manage.py runserver
```


## node build tools -> tailwind, htmx, daisy ui etc

1. in new terminal run the following commands

```python
npm i
```

```python
npm run dev 
```

## Populating database with courses and reviews

```python
python manage.py create_test_courses
```

```python
python manage.py create_random_reviews
```







