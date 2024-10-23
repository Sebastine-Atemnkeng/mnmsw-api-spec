pipeline {
    agent any

    parameters {
        string(name: 'BRANCH_NAME', defaultValue: 'main', description: 'Enter the branch name (e.g., bugfix)')
    }

    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub')
        DOCKER_REPO = "sebastine/project-tsukinome-${params.BRANCH_NAME}"  
        APP_NAME = 'users'
        IMAGE_TAG = 'latest'  // Or use dynamic tagging as mentioned above
    }

    stages {
        stage('Checkout') {
            steps {
                script {
                    checkout([$class: 'GitSCM', branches: [[name: "*/${params.BRANCH_NAME}"]], userRemoteConfigs: [[url: 'https://github.com/Sebastine-Atemnkeng/mnmsw-api-spec.git']]])
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                sh """
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt                
                """
            }
        }

        stage('Unit Test') {
            steps {
                sh """
                    . venv/bin/activate
                    pytest --junitxml=test-results.xml
                """
            }
            post {
                always {
                    junit 'test-results.xml'
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
                    // Define the Docker repo name dynamically using the branch name
                    def dockerRepo = "sebastine/project-tsukinome-${params.BRANCH_NAME}:${BUILD_NUMBER}"

                    try {
                        // Log in to Docker Hub
                        sh "echo ${DOCKERHUB_CREDENTIALS} | docker login -u ${DOCKERHUB_CREDENTIALS} --password-stdin"

                        // Build Docker image
                        sh "docker build -t ${dockerRepo} ."

                        // Push Docker image to the registry
                        sh "docker push ${dockerRepo}"

                        // Optionally clean up the local Docker image
                        sh "docker rmi ${dockerRepo} || true"
                    } catch (Exception e) {
                        echo "Error during Docker image push: ${e.message}"
                        currentBuild.result = 'FAILURE'
                    }
                }
            }
        }
    }

    post {
        always {
            script {
                def colorMap = [
                    SUCCESS: 'good',
                    FAILURE: 'danger',
                    UNSTABLE: 'warning'
                ]
                def buildResult = currentBuild.currentResult
                def color = colorMap[buildResult] ?: 'warning'
                slackSend channel: 'jenkinscicd', color: color, message: "*${buildResult}:* Job ${env.JOB_NAME} build ${env.BUILD_NUMBER} \n More info at: ${env.BUILD_URL}"
            }
        }
    }
}
