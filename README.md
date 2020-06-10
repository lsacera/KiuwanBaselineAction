# Kiuwan Baseline Action
Kiuwan action to perform a baseline analysis.

Usage:
Add the action in any workflow in your repository --> Actions.

Required parameters:
- userid: the username of your kiuwan account (*)
- password: the password of your kiuwan account (*)

Optional parameters:
- kiuwanbaseurl: Kiuwan server used to perform the analysis. The default value is https://www.kiuwan.com
- project name: Name of the project. If not provided, the github repository name is used (owner/project format)
- label: Selected label for the analysis. If not provided, the run number will be used
- databasetype: Database type files in the project, if any. Can be one or more of [none, transacsql, plsql, informix]
- advancedparams: Rest of parameters to be used in the baseline. For a comprehensive list of options, please visit.
https://www.kiuwan.com/docs/display/K5/Kiuwan+Local+Analyzer+CLI+-+Command+Line+Interface

(*) It is higly recommended to use the userid and password as "secrets" of the repository. The secrets can be defined in the Settings options of the repository.
### Important note: We have notified that passwords with special characters as $, are not well propagated as github_secrets, so, we recommend not use special characters if you are using github secrets.

Example of basic usage as step in a workflow:
```
steps:
      - name: Checkout the repository
        uses: actions/checkout@v1
      - name: Kiuwan Baseline Analysis
        uses: lsacera/KiuwanBaselineAction@v1.0
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

Example of basic usage with SSO authentication:
```
    steps:
    # Checks-out your repository under $GITHUB_WORKSPACE, so your job can access it
    - uses: actions/checkout@v1
    - name: Kiuwan Baseline Analysis
      uses: lsacera/KiuwanBaselineAction@v1.0
      with:
          # Name of Kiuwan project
          project: Chess
          # Label for the analysis
          label: '6.3'
          # Username for kiuwan platform
          userid: ${{ secrets.KIUWAN_SSO_USER }}
          # Password for kiuwan platform
          password: ${{ secrets.KIUWAN_SSO_PASSWORD }}
          # Domain ID for SSO accounts  
          advancedparams: ''
          #'--domain-id ${{ secrets.KIUWAN_SSO_DOMAIN }}'
```
