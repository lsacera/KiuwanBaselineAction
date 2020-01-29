# Kiuwan Baseline Action
Kiuwan action to perform a baseline analysis.

Usage:
Add the action in any workflow in your repository --> Actions.

Required parameters:
- project: the name of the application in kiuwan. If it does not exist, it will create a new one.
- userid: the username of your kiuwan account (*)
- password: the password of your kiuwan account (*)

Optional parameters:
- label: the selected label for the analysis. 

(*) It is higly recommended to use the userid and password as "secrets" of the repository. The secrets can be defined in the Settings options of the repository.

Example of usage as step in a workflow:
```
steps:
      - name: Checkout the repository
        uses: actions/checkout@v1
      - name: Kiuwan Baseline Analysis
        uses: lsacera/KiuwanActions@v0.3
        with:
          # Name of Kiuwan project
          project: Personalblog
          # Label for the analysis
          label: version
          # Username for kiuwan platform
          userid: ${{ secrets.KIUWAN_USER }}
          # Password for kiuwan platform
          password: ${{ secrets.KIUWAN_PASS }}
```
