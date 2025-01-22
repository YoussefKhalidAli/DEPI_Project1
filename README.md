# DevOps_Project1

The documentation for the first project of DEPI's DevOps Track.

The following project was configured on ubuntu 22.04 LTS using multipass.

**Week 1**


*Task: Install Jenkins and Docker*

Step 1: Install docker.

    sudo apt update
    sudo apt install docker.io

Step 2: Set up a jenkins server using jenkins image.

Create volume to save jenkins data.

    docker volume create jenkins_data

Build and run the image.

    docker build --name jenkins -p 8080:8080 -p 50000:50000 \
    -v jenkins_data:/var/jenkins_home \
    -v /var/run/docker.sock:/var/run/docker/sock \
    jenkins/jenkins:lts

Expose ports 8080 and 50000.
Mount created volume to jenkins data directory.
Moint the docker socket file to enable jenkins to use docker commands.

Step 3: Open jenkins, authenticate user, and create account.

*Task: Create a basic Dockerized application*

Step 1: Create a directory for the app.
    
    mkdir simpleApp && cd simpleApp

Step 2: Create the app.

    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def hello():
        return "Hello, DEPI!"
        
    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=5000
        
Step 3: Create the image.

    FROM python:3.9-slim

    WORKDIR /app

    COPY . /app

    RUN pip install flask

    CMD ["python", "app.py"]

Step 4: Build the image.

    docker build -t simpleapp .

Step 5: Run the container.

    docker run -d -p 5000:5000 myapp

Step 6: Check if it works by visiting <ip>:5000

If you are using multipass. Find the IP using "multipass info" in your terminal.

*Task: Set up Ansible*

Step 1: Install Ansible

    sudo apt install ansible

Step 2: Create inventory file

    [local]
    localhost ansible_connection=local

"ansible_connection=local" tells ansible that it will work locally without the need for ssh

Step 3: Create playbook

jenkins_setup.yml playbook to automate the jenkins server setup

    - name: Set up jenkins server
      hosts: local
    tasks:
      - name: Install docker
        apt:
          name: docker.io
          state: present

      - name: Pull jenkins image
        shell: docker pull jenkins/jenkins:lts

      - name: Build and run jenkins container
        shell: docker run -d --name jenkins -p 8080:8080 -p 50000:50000 -v jenkins_data:/var/jenkins_home \-v /var/run/docker.sock:/var/run/docker/sock jenkins/jenkins:lts

 simple_app_dockerization.yml playbook to automate the simple web app dockerization

    name: Deploy Dockerized Application
    hosts: local
    tasks:
      - name: Install Docker
        apt:
          name: docker.io
          state: present

    - name: Build simple app image
      shell: cd simpleApp && docker build -t simpleapp .

    - name: Run Docker Container
      shell: docker run -d --name simpleapp -p 5000:5000 simpleapp

