pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub')
        DOCKER_REPO = 'sebastine/project-tsukinome-${env.BRANCH_NAME}'  // Docker repo based on branch name
        APP_NAME = 'users'
        IMAGE_TAG = 'latest'
    }

    stages {
        stage('Checkout') {
            steps {
                script {
                    // Checkout the code and capture the branch name
                    checkout([$class: 'GitSCM', branches: [[name: '*/main']], userRemoteConfigs: [[url: 'https://github.com/Sebastine-Atemnkeng/mnmsw-api-spec.git']]])
                    env.BRANCH_NAME = sh(script: 'git rev-parse --abbrev-ref HEAD', returnStdout: true).trim()
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                sh """
                    # Installing dependencies for the users feature
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt                
                """
            }
        }

        stage('Unit Test') {
            steps {
                sh """
                    # Running unit tests with pytest (or your test framework)
                    pytest --junitxml=test-results.xml
                """
            }
            post {
                always {
                    junit 'test-results.xml'  // Publishing test results
                }
            }
        }

        stage('Code Analysis') {
            environment {
                scannerHome = tool name: 'SONAR_TOKEN'
            }
            steps {
                script {
                    withSonarQubeEnv('SONAR_TOKEN') {
                        sh """
                            ${scannerHome}/bin/sonar-scanner \
                                -Dsonar.projectKey=CSN \
                                -Dsonar.projectName=CSN \
                                -Dsonar.sources=.
                        """
                    }
                }
            }
        }
        stage('Build and Push Docker Image') {
            environment {
                DOCKER_IMAGE = "sebastine/project-tsukinome-${env.BRANCH_NAME}:${BUILD_NUMBER}"
                REGISTRY_CREDENTIALS = credentials('docker-cred')
            }
            steps {
                script {
                    sh 'docker build -t ${DOCKER_IMAGE} .'
                    def dockerImage = docker.image("${DOCKER_IMAGE}")
                    docker.withRegistry('https://index.docker.io/v1/', "docker-cred") {
                        dockerImage.push()
                    }
                    // Optionally clean up
                    sh 'docker rmi ${DOCKER_IMAGE} || true'
                }
            }
        }
    }

    post {
        always {
            script {
                def colorMap = [
                    SUCCESS: 'good',     // Green
                    FAILURE: 'danger',   // Red
                    UNSTABLE: 'warning'  // Yellow (you can add more statuses as needed)
                ]
                def buildResult = currentBuild.currentResult
                def color = colorMap[buildResult] ?: 'warning'
                slackSend channel: 'cybergoat', color: color, message: "*${buildResult}:* Job ${env.JOB_NAME} build ${env.BUILD_NUMBER} \n More info at: ${env.BUILD_URL}"
            }
        }
    }
}