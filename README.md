# Customizable-Ultrasound-Grading-Platform

This application is a dynamic, customizable grading platform for video files, intended to give researchers an open-source, free option for grading and annotating their research data in-house. While the original purpose is intended for grading ultrasound videos, any sort of video can be graded.

The general flow of this GUI is project admin -> graders -> project admin. The project admin will create a study, inputting video files, grading criteria, and grader names. This application will create individualized requests for each inputted grader which the project admin will distribute. Each grader will upload their .zip file to the application, review each assigned video, and send a final spreadsheet with their responses back to the project admin. The project admin will then upload each grader's responses file and download a final spreadsheet with all graded data for use in subsequent statistical analysis.

## Using the GUI

### As Project Admin

Before grading can begin, a team member must take the role of "project administrator"; the project admin will set up the grading on the front end, distribute grade requests, and concatenate the graded data after grading is complete. This person will need to have access to all video files that require grading and the criteria that the graders will be presented for each video.

#### Creating a New Study

When you create a new study, that study is stored into this application's App Data. This means that you'll always be able to re-open the application and see all the previous work that you've done.

1. Consolidate video files into one folder. No other files should be present in this folder. Accepted formats are .mp4 and .avi. Ensure that each video has a unique name.
2. Create a grading schema. This is the rubric that you would like your graders to answer for each video. To do this, make a copy of the provided Excel sheet. Input your criteria, where each criterion is a row in the spreadsheet. For each single-select question type, provide at least two answer options for each criterion; up to ten options for each are accepted. Ensure that all criteria are assigned a question type (single-select).
3. Open the grading application by double-clicking the Ultrasound_Grader_mac.app (or by running python -m ./src/code/main if you're using a development environment and making edits to the GUI).
4. Click "Enter as Admin."
5. Click "Create New Study."
    - Note that there is an example study in the provided distribution
6. Enter your study parameters:
    - Give the study a name
    - Select the folder in which the videos to be graded are stored. The number of videos that the application will incorporate will be auto-detected based on the number of .mp4 and .avi files within the folder. This will be displayed; check that this number fits with your expectations to make sure that no videos are left ungraded.
    - Enter the names of your graders (note that the "Grader Summary" will update in real-time). If you have duplicate names, give those with duplicate names a unique identifier.
    - Select the type of grading paradigm you'd like to employ. The options are to split the number of videos evenly across graders (extra videos (remainder of number of videos/number of graders) will be distributed across the first graders provided) or to have all graders grade all videos. Changing these options will auto-update the "Grader Summary."
    - You also have the option to have graders repeat seeing each video a set number of times. This is advantageous if you wish to examine the intra-rater reliability of your data. Changing these options will auto-update the "Grader Summary.
    - Select the grading schema Excel sheet that you created for this study. The questions and options will be automatically parsed into application. Scroll through the questions and verify that the rubric appears as expected.
7. Click "Create Study."
8. You'll get a success page with the metadata for the study you just created. Read through this and check that everything looks as expected.
9. Click "Release to Graders." This will create a .zip file for each grader for the study. This .zip includes the study metadata and the videos that have been randomly assigned to each grader. Note that these videos will be shown to graders in a blinded, deidentified manner. These .zip files will be automatically sent to your downloads folder.
    - At this point, an optional but recommended step is to go back to the main landing page and click "Enter as Grader," and follow the Annotator/Grader instructions below to test one of the .zip files. Verify that the grading session appears as you'd expect before distributing the grade requests.
10. Click "Back to Admin Landing."
11. Click "Refresh Data" and ensure that the study you just created now appears in the study list.
12. Send each .zip file to their respective grader. They will need to download this application and follow the Annotator/Grader steps provided here.
    - For smaller research applications, the .zip file will be able to be sent via email or uploaded to shared storage service.
    - For larger-scale applications with more videos assigned per grader, you may need to use a large file transfer service or transfer the data via physical hard drive. If these are not viable options and the video data is stored online, alternatives include:
        - Creating multiple studies with identical metadata, but split the master video archive into multiple folders. Graders would have multiple .zips to grade.
        - Unzipping each graders' release file and send the grader the metadata.json file and the CSV files within their specific .zip. They can then download their assigned video files and re-zip everything on their end.

Depending on the study/research design, multiple "studies" within the application may need to be created, if for example:
    - Different videos require different grading criteria (ex. the study collected views of Morrison's pouch and PSAX views of the heart)
    - Different graders should be assigned to specific videos (ex. for "tie-breaker" style study done after a first round of grading, where a third grader only grades disagreements)
    - etc.
In this case, the project admin would need to follow the "Creating a New Study" instructions multiple times, as many time as necessary to fit the study design. This will include separating the master video archive into smaller folders for each "study." The project admin will also need to create a dedicated grading rubric for each.

You can also edit/duplicate previously-created studies. To do this, select the study of interest and click "Edit Selected Study." Rename the study, edit parameters if desired, and release to graders. Renaming the study but not editing any parameters effectively duplicates the study. Be careful to not overwrite previous studies by providing duplicate names!

#### Consolidating Grade Data

After each grader finishes their grade request, they'll receive a file with their response data in their Downloads folder. They will send this file back to you. After you've begun receiving the final grade CSVs (you don't need to wait until all CSVs have been returned to start this process), you can begin consolidating and examining the grade data.

1. Open the application.
2. Click "Enter as Admin."
3. Select the study that you'd like to examine results for.
4. Click "Analyze Results for Selected Study."
5. This opens the results analysis page. If you haven't yet added any grade files for this study, the page will be blank.
6. Click "Add Grader Files."
7. Select the grade data files that you've received thus far for this study. These will populate within the file list associated with this study's results. You can always delete any or all of the selected files.
8. Note that the metadata for the study, including the grader names assigned to this study, will appear in the top left. This allows you to easily check whether all graders for the study are accounted for within the file list.
9. Click "Analyze Data." This can be done regardless of whether or not all graders files are accounted for so that you can analyze results in the interim. The breakdown of grader responses per rubric criterion is shown.
10. Click "Download Concatenated Results." This creates a file that contains all grader responses put into one spreadsheet, sent to your Downloads folder. If you did this without all grader data, you'll only have the data from the spreadsheets uploaded to the study review page.

If you exit the application and come back at a later time with additional grader spreadsheets to add, you won't need to add the previously-uploaded spreadsheets - these are stored within the application's internal data.
S
The consolidated results are designed to be used in subsequent statistical analysis. We encourage all researchers to run an inter-rater (and/or intra-rater, if applicable) reliability analysis on their data for all rubric criteria. The exact statistical method used to examine rater agreement depend upon the study parameters (number of graders per video, if all graders graded all items, etc). Methods to consider (not an exhaustive list) include:

    1. Simple percent agreement calculations
    2. Cohen's kappa (option for weighted)
    3. Fleiss' kappa (option for weighted)
    4. Krippendorf's alpha
    5. Intra-Class Correlation Coefficients
    6. Pearson's r
    7. Spearman's rho
    8. Gwet's AC1/Gwet's AC2

The statistical methods used to examine rater agreement should be decided upon before grading begins. There are many fantastic discussions in the literature on which agreement methods should be used. A few of our favorites are:

    - [McHugh2012]
    - [Stemler2004]

### As Annotator/Grader

All annotators/graders will receive a personalized grade request from the project admin. Typically, this will come in the form of a .zip file. You don't need to do anything with this file other than have it somewhere accessible by your system's file explorer, and it can be deleted after uploading to the application (detailed in steps below). Before beginning grading, ensure that the grading application is installed on your machine; if it isn't, follow the steps provided in the Installation Instructions section. To complete the grade request:

1. Open the application by double-clicking on the .app file.
2. Click "Enter as Grader." This takes you to the grader landing page.
3. Click "Add New Study from Zip."
4. Select the .zip file that you recieved from your project admin. The application will parse the provided data and store the grade request information within its internal data - once finished, you'll receive a success pop-up. At this point, you can safely delete the original .zip file if you'd like.
5. Click the study to show the study metadata. This includes the name of the study, your name, the total number of reviews assigned to you, and the number of questions per video you'll need to answer. Note that it will also show you the number of reviews you've completed so far.
6. With this study selected, click "Begin Grading." This will take you to the grader instructions page. Read through the instructions before beginning. Of particular note, in the original version of this application, you will not be able to go back once you've assigned a grade to each video. It's also recommended to turn your screen brightness up as a high as possible.
7. Click "Start Grading."
8. The grading session will now appear. The majority of the space is occupied by the video player. The video controls are shown underneath the player. The questions you'll need to answer for the video is shown on the right (this section is scrollable - you may need to scroll to answer all questions).
9. When you're ready, press "Play."
10. Answer the questions provided, using the video controls as needed to better inform your responses.
11. Click "Save Grades and Advance to Next Video." This will save your responses and take you to your next assigned video. 
12. Follow this process until all videos have been reviewed. Note that the progress bar at the bottom of the screen shows the number of reviews completed/remaining.
13. You can always exit the grading session and pick up where you left off at a later date. You can test this functionality by reviewing a video, clicking "Save Grades and Advance to Next Video," then clicking "Back to Grader Landing." The metadata for the study you just submitted a grade for should update to show a non-zero number of completed reviews. It should update automatically, but you can always click "Refresh Data" if the completed review isn't showing. Note that the data for each video is only saved once you press the "Save and Advance" button; if you answer the buttons then exit the grader session without clicking "Save and Advance," your responses from that current video won't be saved. Your responses from previous videos WILL be saved.
14. Once you complete all requested reviews, you'll be directed to a "Grading Session Complete" page. Here, you can download your grade data as a CSV. You can also download this data anytime from the Grader Landing page.
15. Send the final grade data CSV back to your project admin.

This is not a web-based application - it is an offline application that saves only to your machine. This means that nobody has access to your grade data until you distribute the final grade file as described in steps 14 and 15 above. Importantly, this also means that if your machine were to be lost/stolen/irreparably broken, your grade data will be lost. This would also happen if you were to re-install/uninstall/delete the application - your progress would be lost!
    - If you're completing a larger grade request, you may wish to store copies of your incomplete grade data at a backed-up location. This can be done by clicking "Download Unfinished Grades" on the Grader Landing page, then placing this file wherever is secure.
    - If you end up in the unfortunate situation of needing to use this backed-up copy on a new machine, you can edit the grade request CSV in the original .zip, deleting rows that reviews you've previously completed. You can then concatenate the two final grade files and send that back to your project admin.

## Installation Instructions

### Downloading the Provided Distribution

We have provided the current, ready-to-use distribution for those who don't want to make edits to the source code. This can simply be downloaded and used immediately.

1. Double-click on the /dist folder on the GitHub repo.
2. Download the Ultrasound_Grader_mac.app file.
3. Double-click the .dmg installer file.
4. Within the installer disk utility, drag the .app file into the Applications folder and give any permissions if prompted.

### Cloning the GUI from GitHub (for Development)

If you want to make edits to the source application code, you can do so by cloning the GitHub repo. Provided in this repo are two virtual environments to suit programmers that prefer Anaconda environments (environment.yml) or Python venv environments (pyvenv.cfg).

1. Clone the GitHub repo.
2. Activate your desired version of the environment from within Customizable-Ultrasound-Grading-Platform.
    - For Anaconda: ```conda env create -f environment.yml```, followed by ```conda activate ultrasoundgradinggui```
    - For Python venv: ```source bin/activate```
3. Make desired edits to GUI
4. Test GUI edits by running ```python -m src.code.main``` from Customizable-Ultrasound-Grading-Platform.
5. To distribute a standalone application with your edits, follow the steps below.

## Creating your own distribution

The distribution for this application is created with PyInstaller using the Virtual Environment created in pyvenv.cfg. The distribution is created with the lightweight venv; If you wish to add any additional dependencies to the distribution, use ```pip install [your package]``` from within this environmentYou can activate the virtual environment by running source bin/activate from Customizable-Ultrasound-Grading-Platform. . When you're ready to create your own distribution, follow the steps below:

1. Make sure you have the relevant virtual environment folders within Customizable-Ultrasound-Grading-Platform:
    - bin/
    - include/
    - lib/
    - pyvenv.cfg
2. Make sure that the venv is up to date with all required dependencies.
3. From the Customizable-Ultrasound-Grading-Platform folder, run ```./build.sh``` to execute the bash script to create a distribution with PyInstaller.
    - If the pyinstall command is not found, be sure you're working in an environment that contains the PyInstaller library. If your environment does not have PyInstaller, run ```pip install pyinstaller```.
    - Note that you do not have to have the virtual environment activated when you run ./build.sh since the shell script will activate it for you.
    - If you want to change any of the parameters for the distribution, you can alter the shell script:
        - --name: the name of the application
        - --icon: the path to the icon, including the icon's filename. Icon must be type .icns on MacOS
        - --onedir: tells PyInstaller to create both an executable file and a folder with all supporting libraries and dependencies already unpacked for faster runtime. The other popular option for PyInstaller is --onefile, which bundles everything into one single file for readability and simple distribution, but with the disadvantage of longer startup time to unpack and load dependencies (which takes longer for large dependency libraries, such as PyQt and pandas, as used here)
4. A successful build from PyInstaller will result in a "Build complete!" message. Before distributing the application, you should test the app by running it. From Customizable-Ultrasound-Grading-Platform, run ```./dist/Ultrasound_Grader_mac.app/Contents/MacOS/Ultrasound_Grader_mac```. If you changed the name of the distribution, rename the path accordingly. Note that you won't be able to enter the .app from Finder, but you can enter it from terminal and an IDE(we use VSCode). This command will run the executable for the application.
5. Should you wish to iterate on the code, you can change the source code, run ```./build.sh``` again, (answering yes to both checks from PyInstaller to remove previous builds), then test the new version with ```./dist/Ultrasound_Grader_mac.app/Contents/MacOS/Ultrasound_Grader_mac```. Any error handling and print statements will show in the terminal for debugging.
6. Do a final test of the application by double-clicking the .app file in Finder.
7. When you're ready to distribute the code, you'll need to zip the .app and send it out. For MacOS, end users may have permissions issues when attempting to run the app. We recommend creating a .dmg file to help users install the .app with the necessary permissions. To create a DMG:
    - Copy your .app to a new folder?
    - Open the native Disk Utility app that comes with MacOS
    - Select File -> New Image -> Image From Folder
    - Select the folder where you have placed the app
    - Give the .dmg a name [we suggest something like "Ultrasound Grader Installer"] and press save - this creates a distributable image
    - If needed you can add a link to applications to DMG. It helps user in installing by drag and drop. Do this from within the terminal on Mac? 

## Development Information

Application Author: Victoria Hurd

Last Updated: 2/3/2026

Development Information:

    - MacOS Sequoia v15.6.1
    - Apple M1 chip
    - Python 3.11
    - Development Environment: VSCode, v1.108.1
    - Package Manager: conda, v24.11.3

Notes:

    - only tested for compatibility with MacOS
    - distribution created with PyInstaller
