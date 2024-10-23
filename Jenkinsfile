pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub')
        APP_NAME = 'users'
        IMAGE_TAG = 'latest'
    }

    stages {
        stage('Checkout') {
            steps {
                script {
                    // Checkout the code and capture the branch name
                    checkout([$class: 'GitSCM', branches: [[name: '*/main']], userRemoteConfigs: [[url: 'https://github.com/Sebastine-Atemnkeng/mnmsw-api-spec.git']]])
                    env.BRANCH_NAME = sh(script: 'git rev-parse --abbrev-ref HEAD', returnStdout: true).trim().toLowerCase()
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
                    . venv/bin/activate
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
            steps {
                script {
                    // Defining the Docker repo name dynamically using the lowercase branch name
                    def dockerRepo = "sebastine/project-tsukinome-${env.BRANCH_NAME}:${BUILD_NUMBER}"

                    // Build Docker image
                    sh "docker build -t ${dockerRepo} ."

                    // Push Docker image to the registry
                    def dockerImage = docker.image("${dockerRepo}")
                    docker.withRegistry('https://index.docker.io/v1/', "dockerhub") {
                        dockerImage.push()
                    }

                    // Optionally clean up the local Docker image
                    sh "docker rmi ${dockerRepo} || true"
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
