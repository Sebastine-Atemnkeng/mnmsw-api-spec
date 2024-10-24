pipeline {
    agent any

    parameters {
        string(name: 'BRANCH_NAME', defaultValue: '', description: 'Enter the branch name (e.g., bugfix)')
    }

    environment {
        registryCredential = 'dockerhub'
        registry = "sebastine/project-tsukinome-${params.BRANCH_NAME}"  
        dockerImage = ''  // Or use dynamic tagging as mentioned above
        GITHUB_TOKEN = credentials('github-token') // GitHub token for pulling version information
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

        stage('Get Version') {
            steps {
                script {
                    // Retrieve the latest version from Git
                    VERSION = sh(script: "git describe --tags --abbrev=0", returnStdout: true).trim()
                    echo "Version is: ${VERSION}"
                }
            }
        }

        stage('Build and Push Docker Image') {
            steps {
                script {
                    // Define the Docker repo name dynamically using the branch name
                    withCredentials([usernamePassword(credentialsId: 'dockerhub', passwordVariable: 'DOCKERHUB_PASSWORD', usernameVariable: 'DOCKERHUB_USERNAME')]) {
                        def dockerRepo = "sebastine/project-tsukinome-${params.BRANCH_NAME}:${VERSION}"

                        try {
                            // Log in to Docker Hub
                            sh "echo \$DOCKERHUB_PASSWORD | docker login -u \$DOCKERHUB_USERNAME --password-stdin"

                            // Build Docker image
                            dockerImage = docker.build("${registry}:${VERSION}")

                            // Push Docker image to the registry
                            dockerImage.push()

                            // Optionally clean up the local Docker image
                            sh "docker rmi ${registry}:${VERSION} || true"
                        } catch (Exception e) {
                            echo "Error during Docker image push: ${e.message}"
                            currentBuild.result = 'FAILURE'
                        }
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
                slackSend channel: 'jenkinscicd', color: color, message: "*${buildResult}:* Job ${env.JOB_NAME} build ${VERSION} \n More info at: ${env.BUILD_URL}"
            }
        }
    }
}
