# dsd project repo
PRIVATE School-Project about Distributed Systems.

## Usage (for dsd_project)

Main Branch: The code that is merged after being reviewed. The main branch code should always be runnable without errors.

Develop Branch: Branch where the code is pushed. This is the branch we push to after making changes to the code.

Feature Branch: Testing purposes, if we want to test a different concept. 




Dont forget to change to develop or feature branch before making changes to code. Always push to a "develop" or "feature" branch. Code will be reviewed by another in team to make sure its working properly before merging to the main branch. (Good practice to let someone else review your code, if change is minor, its okay to merge)

To stay updated with the latest code changes and collaborate effectively, please follow these guidelines:

1. **Update Your Local Branch**:
   - Regularly update your local branch with the latest changes from the remote repository. You can do this using the following command:
     ```
     git pull origin <branch-name>
     ```
   - Replace `<branch-name>` with the name of the branch you're working on.
     
2. **Commit and Push Frequently**:
   - After each coding session or when you make significant changes, commit and push your changes to the repository (feature branch). This ensures that other participants can access your work and collaborate effectively. (Please also make sure your code is working, if not, create an issue)
   - Use descriptive commit messages to provide context about the changes you've made.
   - (To be able to review the code easier, and decide if we will merge it into the main branch, a good detailed description that explains the new change would be very helpful, to understand the contribution.)

3. **Collaboration**:
   - If you encounter any issues or have questions about the project, feel free to reach out to other participants or create an issue on the repository.
   - Collaboration is key to the success of the project, so make sure to communicate and coordinate with other contributors.
  
## Userful Commands - Explained

   - Update local branch (do this every coding session). Main or develop. Note: Main / develop branch may have different code. Please check which one you want to build on.
     ```
     git pull origin <branch-name>
     ```
     
   - Chech which branches you have on your local repo and which branch you are in.
     ```
     git branch
     ```
     
   - Change current branch
     ```
     git checkout <branch-name>
     ```
     
   - See modifications made during your coding session.
     ```
     git status
     ```
     
   - Add modified files to your commition
     ```
     git add <modified-file-name>
     ```
   - Commit added files. Write a commit message with title and description on what changes you have made and why. Add issue if needed. If no issue, write: "Issue: None" in the end of commit message.
     ```
     git commit
     ```
   - Push commit to repo on github. Push to develop.
     ```
     git push origin <branch-name>
     ```
     

## Additional Information

- If you're new to Git or need help with any of the commands mentioned above, refer to online resources or documentation for more detailed instructions.
- Remember to adhere to any coding standards or guidelines established for the project to maintain consistency and readability.
