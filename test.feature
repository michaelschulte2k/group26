Feature Tests for User Stories

Feature 1: Attaching an image to a project/task
Description: Allows the user to upload an image file (.jpg, .png, .gif, etc.) to a project
Feature Tests:
1. Verify that the file type of the picture that the user is uploading is compatible. Compatible file types: .jpg, .jpeg, .png, .gif, .pdf
2. Verify that the file size isn’t too big. Size limits at 4000 x 4000 (example)
3. Verify that the user is able to cancel the current upload action. Have a button there for the user to cancel and close out the file upload window.
4. Verify that the file the user just attempted to upload is the correct one. Give the user a popup that asks them if the file they chose is the file they want to upload.
Feature 2: User Login
Description: The login stage of our program is probably the most vulnerable to attack. Therefore we have to take proper testing measures for security. A user must not be able to enter a certain range of characters and there should be a timeout feature.
1.  Verify if a user cannot enter the characters more than the specified range in each field (Username and Password).
Test Example: abcdefghiJkLmnoPqrSTuvwyxyZ123456789
2.  Verify the timeout functionality of the login session.
Test Example: Wait time set to: 5mins
3.  Verify if a user should not be allowed to log in with different credentials from the same browser at the same time.
Test Example: Use script to sign in user with two test accounts
4.  Verify if a user should be able to login with the same credentials in different browsers at the same time.
Test Example: Create two virtual login attempts that login into the same account

Feature 3: Reacting to comments on Projects/Tasks (5-star rating system)
Description: Allows the user to react to comments with a star rating system or a emoji based system (Similar to Discord maybe?)
1. Verify that the user is selecting a comment to react to.
2. Verify that the user is using an emoji/star rating to react to comments.
3. Verify that the user is able to un-react to comments. Maybe have an X for the user to press to remove it.

Feature 4: Assigning a team member to a project
Verify that a user is not already on a different team. Cause an error message if it happens
Verify that there is space for the user on the team
Verify that there can not be more than x amount of people on the team
	Test Example: set limit to 10 people 
Verify that there is only select administrators for the company, making sure that the member cannot leave the group. 

