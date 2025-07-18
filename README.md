# utlectives instructions


1. Git clone repository

```python
git clone git clone --branch filter-rewrite --single-branch https://github.com/charmandercodes/utlectives.git . && rm -rf .git
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

----------

8. Open new terminal and run (for node build tools -> tailwind, htmx, daisy ui etc)

```python
npm run dev 
```


