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


*Task: Pipeline Plan*

Create a pipeline to re-dockerize the simple web app everytime the app.py file is changed.
Jenkins will pull the git repo every 5 minutes and check if a change was made to the simpleApp/app.py file. If so, it will run the simple_app_dockerization.yml playbook to re-dockerize the app.


**Week 2**

*Tasks: Create Jenkins Jobs and Integrate Git*

Step 1: Create a jenkmins pipeline job.

Step 2: Set it to pull the githube repo every five minutes by choosing POLL SCM and enter.

    H/5 ****

Step 3: Create a pipeline to run the simple_app_dockerization.yml playbook everytime the simpleApp/app.py file is changed.

    pipeline {
        agent any

        stages {
            stage('Checkout Code') {
                steps {
                    git url: 'https://github.com/YoussefKhalidAli/DEPI_Project1.git', branch: 'main'
                }
            }

            stage('Detect Changes in app.py') {
                steps {
                    script {
                        def changes = sh(script: "git diff --name-only HEAD~1 HEAD", returnStdout: true).trim()

                        if (!changes.contains('simpleApp/app.py')) {
                            echo 'No changes detected in simpleApp/app.py. Skipping build.'
                            currentBuild.result = 'SUCCESS'
                            return
                        } else {
                            echo 'Changes detected in simpleApp/app.py. Proceeding with the build.'
                        }
                    }
                }
            }
            stage('Run Ansible Playbook') {
                steps {
                    sh """
                    ansible-playbook -i inventory simple_app_dockerization.yml
                    """
                }
            }
        }

        post {
            always {
                echo 'Pipeline execution completed.'
            }
            success {
                echo 'Job ran successfully.'
            }
            failure {
                echo 'Job failed.'
            }
        }
    }


*Task: Automated Testing*

Add the following stage after 'Run Ansible Playbook' to test the execution of the playbook.

            stage('Test Deployment with curl') {
                        steps {
                            script {
                                def server_ip = '172.22.107.42'
    
                                def curl_output = sh(script: "curl -s http://${server_ip}:5000", returnStdout: true).trim()
    
                                if (!curl_output.contains('Hello, DevOps!')) {
                                    error("Flask app is not running correctly. Response: ${curl_output}")
                                } else {
                                    echo "Flask app is running correctly. Response: ${curl_output}"
                                }
                            }
                        }
            }

*Task: Set Up Notifications*

Step 1: Install the email extended plugin.

Step 2: Go to manage jenkins -> system and scroll down to email notification. Add your username (email) and password (gmail generated app password), choose SSL and port number 465.

Step 3: Scroll up to extended email notification. Create jenkins credintial using your username and password, set id to 'gmailcredintials' save the changes and add this to the 'always' code in the 'post' segment in the piepline.

        emailext (
                    subject: "Jenkins Build ${currentBuild.currentResult}: Job ${env.JOB_NAME} (${env.BUILD_NUMBER})",
                    body: """
                        Pipeline execution completed.
                        Build Result: ${currentBuild.currentResult}
                        Job: ${env.JOB_NAME}
                        Build Number: ${env.BUILD_NUMBER}
                        Build URL: ${env.BUILD_URL}
                    """,
                    to: '<your-email>'
                )

**Week 3**

*Task: Integrate Docker Hub or private registry*

Step 1: Create 2 docker hub repositeries, one for the simple app (<username>/simpleapp) and one for the custom jenkins image (<username/my-jenkins-ansible).

Step 2: Tag the images 

    docker tag simpleapp:latest <username>/simpleapp:v1.0

    docker tag my-jenkins:lts-ansible <username>/my-jenknins-ansible:v1.0

Step 3: Push the images

    docker push <username>/simpleapp:v1.0

    docker push <username>/my-jenknins-ansible:v1.0

