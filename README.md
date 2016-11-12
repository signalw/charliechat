CharlieChat  
============
[ ![Codeship Status for signalw/charliechat](https://codeship.com/projects/0c13aeb0-8b25-0134-d3b4-7a22352218be/status?branch=master)](https://codeship.com/projects/184590)

CharlieChat is a project for the course CS136a - Automated Speech Recognition at Brandeis Univerisity.

We are trying to create a web application that allows users to request MBTA information and give possible transportation options for them.

### Cloud production
https://mbtachat.herokuapp.com

### Local development setup
Steps below assume we are in UNIX environment. Windows users can use Cygwin, Git Bash, etc. to achieve similar functionalities.

We recommend using `pip` and `virtualenv` to manage python dependencies, if they are not installed yet:

    sudo easy_install pip
    sudo pip install virtualenv

Now we change into the root directory as it has been cloned from git and install the python dependencies:

    cd charliechat
    virtualenv venv      # creates a new virtual environment  in ./venv
    source venv/bin/activate  # activates the virtual environment
    pip install -r requirements.txt  # installs the python dependencies

While in virtual environment, run server by calling:

    python manage.py runserver   # Runs the local development server
    python3 manage.py runserver   # Python3 is recommended, if the default interpreter is not

Now the local host should be listening to port 8000 by default. To exit, hit "Ctrl+C".

To exit virtual environment:

    deactivate    # deactivates the virtual environment

### Authors

* Jessica Huynh
* Heather Lourie
* Xinhao Wang
* Thomas Zhang

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
