# Created by renzo at 1/16/25
Feature: Functions
  # Enter feature description here

  @api @functions @regression @apiOperation:config_v1_orgs_projects_functions_create
  Scenario: Create function using an invalid token [401]
    Given I create a project with name "test_project_function_created_invalid_token"
    Then I expect a created successfully as result
    Given I am using a fake token
    When I create a random function for project "test_project_function_created_invalid_token"
    Then I expect an error as result
    And I expect to have 401 as code from response
    And I expect to have an error message about invalid token

  @api @functions @regression @sanity @smoke
  Scenario: Create function without using a token [401]
    Given I create a project with name "test_project_function_created_no_token"
    Then I expect a created successfully as result
    Given I am not authenticated
    When I create a random function for project "test_project_function_created_no_token"
    Then I expect an error as result
    And I expect to have 401 as code from response
    And I expect to have an error message about invalid credentials

  @api @functions @regression
  Scenario: Create function without value for body [400]
    Given I create a project with name "test_project_function_without_data"
    Then I expect a created successfully as result
    Given I create a function with this data "{}" for project "test_project_function_without_data"
    Then I expect an error as result
    And I expect to have 400 as code from response
    And I expect to have this alert "This field is required" for "name" field
    And I expect to have this alert "This field is required" for "sql" field

  @api @functions @regression @delete_shared_resource
  Scenario Outline: Create function without values [400]
    # Create function without value for name [400]
    # Create function without value for sql [400]
    # Create function with object inside [400]
    # Create function name with distinct characters [400]
    Given I create a project with name "test_project_function_without_values" just one time
    Then I expect a created successfully as result
    Given I create a function with this data "<function>" for project "test_project_function_without_values"
    Then I expect an error as result
    And I expect to have 400 as code from response
    And I expect to have this alert "<alert>" for "<field>" field
    Examples:
    | function                                                                                                                           | field            | alert                                                         |
    | {"name":"test_function","sql":""}                                                                                                  | sql              | This field may not be blank                                   |
    | {"name":"","sql":"SELECT * FROM test_project_function_without_values.test_table_venom_functions FORMAT JSON"}                      | name             | This field may not be blank                                   |
    | [{"name":"test_function","sql":"SELECT * FROM test_project_function_without_values.test_table_venom_functions FORMAT JSON"}]       | non_field_errors | Invalid data. Expected a dictionary, but got list             |
    | {"name":"test_function'-*/?@#$","sql":"SELECT * FROM test_project_function_without_values.test_table_venom_functions FORMAT JSON"} | name             | Name can only contain alphanumeric characters and underscores |

  @api @functions @regression
  Scenario: Create function inside a non existing organization [404]
    Given I create a project with name "test_project_function_created_wrong_org"
    Then I expect a created successfully as result
    Given I try to work with a non existing organization
    When I create a random function for project "test_project_function_created_wrong_org"
    Then I expect an error as result
    And I expect to have 404 as code from response
    And I expect to have this alert "Not found" for "detail" field

  @api @functions @regression
  Scenario Outline: Create function by using an invalid project [404]
    Given I create a function with id "test_function" for project id "<project_id>"
    Then I expect an error as result
    And I expect to have 404 as code from response
    And I expect to have this alert "Not found" for "detail" field
    Examples:
    | project_id |
    | 123        |
    | fakeId     |

  @api @functions @regression @sanity @smoke @apiOperation:config_v1_orgs_projects_functions_create
  Scenario: Create function [201]
    Given I create a project with name "test_project_function_valid_token"
    Then I expect a created successfully as result
    Given I create a function with this data "{"name":"test_function","description": "test function","sql":"SELECT * FROM test_project_function_valid_token.test_table_venom_functions FORMAT JSON"}" for project "test_project_function_valid_token"
    Then I expect a created successfully as result
    And Comparing with response at position 2, I expect to have this value "<current_resource.id>" in "project" field
    And I expect to have this value "test_function" in "name" field
    And I expect to have this value "test function" in "description" field
    And I expect to have this value "SELECT * FROM test_project_function_valid_token.test_table_venom_functions FORMAT JSON" in "sql" field
    And I expect to have 201 as code from response

  @api @functions @regression
  Scenario: Create function with required data [201]
    Given I create a project with name "test_project_function_required_param"
    Then I expect a created successfully as result
    Given I create a function with this data "{"name":"test_function","sql":"SELECT * FROM test_project_function_required_param.test_table_venom_functions FORMAT JSON"}" for project "test_project_function_required_param"
    Then I expect a created successfully as result
    And I expect to have 201 as code from response
    And I expect to have this value "test_function" in "name" field
    And I expect to not have a value in "description" field
    And I expect to have this value "SELECT * FROM test_project_function_required_param.test_table_venom_functions FORMAT JSON" in "sql" field
    And I expect to have a value in "url" field
    And I expect to have a value in "created" field
    And I expect to have a value in "modified" field
    And I expect to have a value in "publish_task_id" field

  @api @functions @regression
  Scenario: Create function with a repeat name [400]
    Given I create a project with name "test_project_function_repeat_name"
    Then I expect a created successfully as result
    Given I create a function with this data "{"name":"test_function","description":"test function","sql":"SELECT * FROM test_project_function_repeat_name.test_table_venom_functions FORMAT JSON"}" for project "test_project_function_repeat_name"
    Then I expect a created successfully as result
    When I create a function with name "test_function" for project "test_project_function_repeat_name"
    Then I expect an error as result
    And I expect to have 400 as code from response
    And I expect to have this alert "test_function already exists as a name within the specified project_id." for "name" field

  @api @functions @regression @sanity @smoke @apiOperation:config_v1_orgs_projects_functions_bulk_function_create
  Scenario: Create bulk function [201]
    Given I create a project with name "test_project_bulk_function_valid_token"
    Then I expect a created successfully as result
    Given I create a bulk function with this data "[{"name":"test_function_1","sql": "SELECT * from test_project_bulk_function_valid_token.test_table"},{"name":"test_function_2","sql":"SELECT * from test_project_bulk_function_valid_token.test_table"}]" for project "test_project_bulk_function_valid_token"
    Then I expect a created successfully as result
    And I expect to have 201 as code from response

  @api @functions @regression
  Scenario: Create bulk function with an existing name [400]
    Given I create a project with name "test_project_bulk_function_existing_name"
    Then I expect a created successfully as result
    Given I create a bulk function with this data "[{"name":"test_function_1","sql": "SELECT * from test_project_bulk_function_existing_name.test_table"},{"name":"test_function_2","sql":"SELECT * from test_project_bulk_function_existing_name.test_table"}]" for project "test_project_bulk_function_existing_name"
    Then I expect a created successfully as result
    Given I create a bulk function with this data "[{"name":"test_function_1","sql": "SELECT * from test_project_bulk_function_existing_name.test_table"},{"name":"test_function_2","sql":"SELECT * from test_project_bulk_function_existing_name.test_table"}]" for project "test_project_bulk_function_existing_name"
    Then I expect an error as result
    And I expect to have 400 as code from response
    And I expect to have this alert "[{"name":["test_function_1 already exists as a name within the specified project_id."]},{"name":["test_function_2 already exists as a name within the specified project_id."]}]"

  @api @functions @regression
  Scenario Outline: Create bulk function without values [400]
    # Create bulk function with distinct characters [400]
    # Create bulk function without value for name [400]
    # Create bulk function without value for sql [400]
    # Create bulk function without value for dictionary body [400]
    Given I create a project with name "<project_name>"
    Then I expect a created successfully as result
    Given I create a bulk function with this data "<function>" for project "<project_name>"
    Then I expect an error as result
    And I expect to have 400 as code from response
    And I expect to have this alert "<alert>"
    Examples:
    | function                                                                                                            | alert                                                                             | project_name                                    |
    | [{"name":"test_function_1$%&/(!","sql": "SELECT * from test_project_bulk_function_distinct_characters.test_table"}] | {"name":["Name can only contain alphanumeric characters and underscores"]}        | test_project_bulk_function_distinct_characters  |
    | [{"name": "","sql": "SELECT * from test_project_bulk_function_without_name.test_table"}]                            | {"name":["This field may not be blank."]}                                         | test_project_bulk_function_without_name         |
    | [{"name": "test_function_1","sql": ""}]                                                                             | {"sql":["This field may not be blank."]}                                          | test_project_bulk_function_without_sql          |
    | [{"name": "","sql": ""}]                                                                                            | {"name":["This field may not be blank."],"sql":["This field may not be blank."]}  | test_project_bulk_function_without_dictionary   |

  @api @functions @regression
  Scenario: Create bulk function with repeat name [400]
    Given I create a project with name "test_project_bulk_function_repeat_name"
    Then I expect a created successfully as result
    Given I create a bulk function with this data "[{"name":"test_function_1","sql": "SELECT * from test_project_bulk_function_repeat_name.test_table"},{"name":"test_function_1","sql":"SELECT * from test_project_bulk_function_repeat_name.test_table"}]" for project "test_project_bulk_function_repeat_name"
    Then I expect an error as result
    And I expect to have 400 as code from response
    And I expect to have this alert "Request body contains repeated function names" for "name" field

  @api @functions @regression
  Scenario: Create single function in a bulk function [201]
    Given I create a project with name "test_project_bulk_function_single_function"
    Then I expect a created successfully as result
    Given I create a bulk function with this data "[{"name":"test_function","sql": "SELECT * from test_project_bulk_function_single_function.test_table"}]" for project "test_project_bulk_function_single_function"
    Then I expect a created successfully as result
    And I expect to have 201 as code from response

  @api @functions @regression
  Scenario: Create bulk function without value for list body [400]
    Given I create a project with name "test_project_bulk_function_without_list_body"
    Then I expect a created successfully as result
    Given I create a bulk function with this data "[]" for project "test_project_bulk_function_without_list_body"
    Then I expect an error as result
    And I expect to have 400 as code from response
    And I expect to have this alert "This list may not be empty" for "non_field_errors" field

  @api @functions @regression @smoke @sanity @apiOperation:config_v1_orgs_projects_functions_retrieve
  Scenario: Get function [200]
    Given I create a project with name "test_project_function_get_valid_token"
    Then I expect a created successfully as result
    Given I create a function with this data "{"name":"test_function","description":"test function","sql":"SELECT * FROM test_project_function_get_valid_token.test_table_venom_functions FORMAT JSON"}" for project "test_project_function_get_valid_token"
    Then I expect a created successfully as result
    When I get the function with name "test_function" for project with name "test_project_function_get_valid_token"
    Then I expect to have 200 as code from response
    And I expect to have this value "test_function" in "name" field
    And I expect to have this value "test function" in "description" field
    And I expect to have this value "SELECT * FROM test_project_function_get_valid_token.test_table_venom_functions FORMAT JSON" in "sql" field

  @api @functions @regression @sanity @smoke
  Scenario: Get function without using a token [401]
    Given I create a project with name "test_project_function_get_no_token"
    Then I expect a created successfully as result
    Given I create a function with this data "{"name":"test_function","description":"test function","sql":"SELECT * FROM test_project_function_get_no_token.test_table_venom_functions FORMAT JSON"}" for project "test_project_function_get_no_token"
    Then I expect a created successfully as result
    Given I am not authenticated
    When I get the function with name "test_function" for project with name "test_project_function_get_no_token"
    Then I expect an error as result
    And I expect to have 401 as code from response
    And I expect to have "Authentication credentials were not provided." as error message

  @api @functions @regression
  Scenario: Get function using an invalid token [401]
    Given I create a project with name "test_project_function_get_invalid_token"
    Then I expect a created successfully as result
    Given I create a function with this data "{"name":"test_function","description":"test function","sql":"SELECT * FROM test_project_function_get_invalid_token.test_table_venom_functions FORMAT JSON"}" for project "test_project_function_get_invalid_token"
    Then I expect a created successfully as result
    Given I am using a fake token
    When I get the function with name "test_function" for project with name "test_project_function_get_invalid_token"
    Then I expect an error as result
    And I expect to have 401 as code from response
    And I expect to have an error message about invalid token

  @api @functions @regression
  Scenario Outline: Get function by using an invalid function [404]
#    Given I create a project with name "test_project_function_get_wrong_function"
#    Then I expect a created successfully as result
    When I get the function with id "<function_id>" for project with id "test_project_function_get_wrong_function"
    Then I expect an error as result
    And I expect to have 404 as code from response
    And I expect to have "Not found." as error message
    Examples:
    | function_id |
    | 123        |
    | fakeId     |

  @api @functions @regression
  Scenario Outline: Get function by using an invalid project [404]
    When I get the function with id "fake123" for project with id "<project_id>"
    Then I expect an error as result
    And I expect to have 404 as code from response
    And I expect to have this alert "Not found" for "detail" field
    Examples:
    | project_id |
    | 123        |
    | fakeId     |
    |            |

  @api @functions @regression
  Scenario: Get function inside a non existing organization [404]
    Given I create a project with name "test_project_function_get_wrong_org"
    Then I expect a created successfully as result
    When I create a function with name "test_function_get_wrong_org" for project "test_project_function_get_wrong_org"
    Then I expect a created successfully as result
    Given I try to work with a non existing organization
    When I get the function with name "test_function_get_wrong_org" for project with name "test_project_function_get_wrong_org"
    Then I expect an error as result
    And I expect to have 404 as code from response
    And I expect to have "Not found." as error message

  @api @functions @regression @smoke @sanity @apiOperation:config_v1_orgs_projects_functions_list
  Scenario: Get functions [200]
    Given I create a project with name "list_functions"
    Then I expect a created successfully as result
    Given I create a function with this data "{"name":"test_function1","description":"test function1","sql":"SELECT * FROM list_functions.test_table_venom_functions FORMAT JSON"}" for project "list_functions"
    Then I expect a created successfully as result
    Given I create a function with this data "{"name":"test_function2","description":"test function2","sql":"SELECT * FROM list_functions.test_table_venom_functions FORMAT JSON"}" for project "list_functions"
    Then I do not expect an error as result
    When I get all the functions for project with name "list_functions"
    Then I expect to have 200 as code from response
    Then From a list of elements of the response, extract who is in position 1
    And I expect to have this value "test_function2" in "name" field
    And I expect to have this value "test function2" in "description" field
    And I expect to have this value "SELECT * FROM list_functions.test_table_venom_functions FORMAT JSON" in "sql" field
    And I expect to have values in "url, uuid, created, modified" fields
    Then From responses, move to front response in position 2
    Then From a list of elements of the response, extract who is in position 2
    And I expect to have this value "test_function1" in "name" field
    And I expect to have this value "test function1" in "description" field
    And I expect to have this value "SELECT * FROM list_functions.test_table_venom_functions FORMAT JSON" in "sql" field
    And I expect to have values in "url, uuid, created, modified" fields

  @api @functions @regression @sanity @smoke
  Scenario: Get functions without using a token [401]
    Given I create a project with name "test_project_function_find_all_without_token"
    Then I expect a created successfully as result
    Given I am not authenticated
    When I get all the functions for project with name "test_project_function_find_all_without_token"
    Then I expect an error as result
    And I expect to have 401 as code from response
    And I expect to have an error message about invalid credentials

  @api @functions @regression
  Scenario: Get functions using an invalid token [401]
    Given I create a project with name "test_project_function_find_all_invalid_token"
    Then I expect a created successfully as result
    Given I am using a fake token
    When I get all the functions for project with name "test_project_function_find_all_invalid_token"
    Then I expect an error as result
    And I expect to have 401 as code from response
    And I expect to have an error message about invalid token

  @api @functions @regression
  Scenario Outline: Get functions by using an invalid project [404]
    When I get all the functions for project with id "<project_id>"
    Then I expect an error as result
    And I expect to have 404 as code from response
    And I expect to have this alert "Not found" for "detail" field
    Examples:
    | project_id |
    | 123        |
    | fakeId     |
    |            |

  @api @functions @regression
  Scenario: Get functions inside a non existing organization [404]
    Given I create a project with name "test_project_function_find_all_fake_org"
    Then I expect a created successfully as result
    Given I try to work with a non existing organization
    When I get all the functions for project with name "test_project_function_find_all_fake_org"
    Then I expect an error as result
    And I expect to have 404 as code from response
    And I expect to have this alert "Not found" for "detail" field

  @api @functions @regression @sanity @smoke @delete_shared_resource @apiOperation:config_v1_orgs_projects_functions_update @apiOperation:config_v1_orgs_projects_functions_partial_update
  Scenario Outline: Update function [200]
    Given I create a project with name "test_project_function_upd_valid_token" just one time
    Then I expect a created successfully as result
    Given I create a function with name "<function_name>" and sql "SELECT * FROM test_project_function_upd_valid_token.test_function_venom_functions FORMAT JSON" for project "test_project_function_upd_valid_token" just one time
    Then I expect a created successfully as result
    When Via <update_method> I change the function with name "<function_name>" that belongs to project with name "test_project_function_upd_valid_token" using as name "<new_name>", as description "test function" and as sql "SELECT * FROM test_project_function_upd_valid_token.test_table_venom_functions FORMAT JSON" as new data
    Then I expect to have 200 as code from response
    And I expect to have this value "<new_name>" in "name" field
    And I expect to have this value "test function" in "description" field
    And I expect to have this value "SELECT * FROM test_project_function_upd_valid_token.test_table_venom_functions FORMAT JSON" in "sql" field
    And I expect to have values in "url, uuid, created, modified" fields
    And I expect to have a value in "publish_task_id" field
    Examples:
      | update_method | function_name                       | new_name  |
      | PUT           | test_function_put_upd_valid_token   | new_put   |
      | PATCH         | test_function_patch_upd_valid_token | new_patch |

  @api @functions @regression @delete_shared_resource
  Scenario Outline: Update function using an invalid token [401]
    Given I create a project with name "test_project_function_upd_invalid_token" just one time
    Then I expect a created successfully as result
    When I create a function with name "<function_name>" for project "test_project_function_upd_invalid_token"
    Then I expect a created successfully as result
    Given I am using a fake token
    When Via <update_method> I change the function with name "<function_name>" that belongs to project with name "test_project_function_upd_invalid_token" using as name "new_name" as new data
    Then I expect an error as result
    And I expect to have 401 as code from response
    And I expect to have an error message about invalid token
    Examples:
      | update_method | function_name                         |
      | PUT           | test_function_put_upd_invalid_token   |
      | PATCH         | test_function_patch_upd_invalid_token |

  @api @functions @regression @sanity @smoke @delete_shared_resource
  Scenario Outline: Update function without using a token [401]
    Given I create a project with name "test_project_function_upd_no_token" just one time
    Then I expect a created successfully as result
    When I create a function with name "<function_name>" for project "test_project_function_upd_no_token"
    Then I expect a created successfully as result
    Given I am not authenticated
    When Via <update_method> I change the function with name "<function_name>" that belongs to project with name "test_project_function_upd_no_token" using as name "new_name" as new data
    Then I expect an error as result
    And I expect to have 401 as code from response
    And I expect to have an error message about invalid credentials
    Examples:
      | update_method | function_name                    |
      | PUT           | test_function_put_upd_no_token   |
      | PATCH         | test_function_patch_upd_no_token |

  @api @functions @regression @delete_shared_resource
  Scenario Outline: Update function without value for body [400]
    Given I create a project with name "test_project_upd_without_body" just one time
    Then I expect a created successfully as result
    When I create a function with name "<function_name>" and sql "SELECT * FROM test_project_upd_without_body.test_function_venom_functions FORMAT JSON" for project "test_project_upd_without_body" just one time
    Then I expect a created successfully as result
    When Via <update_method> I change the function with name "<function_name>" that belongs to project with name "test_project_upd_without_body" using as name " " and as sql " " as new data
    Then I expect an error as result
    And I expect to have 400 as code from response
    And I expect to have this alert "This field may not be blank." for "name" field
    And I expect to have this alert "This field may not be blank." for "sql" field
    Examples:
      | update_method | function_name                        |
      | PUT           | test_function_put_upd_without_body   |
      | PATCH         | test_function_patch_upd_without_body |

  @api @functions @regression @delete_shared_resource
  Scenario Outline: Update function without values [400]
    # Update function without value for name [400]
    # Update function without value for sql [400]
    # Update function with object inside [400]
    # Update function name with distinct characters [400]
    Given I create a project with name "test_project_function_upd_without_values" just one time
    Then I expect a created successfully as result
    When I create a function with this data "<data>" for project "test_project_function_upd_without_values"
    Then I expect a created successfully as result
    When Via <update_method> I change the function with name "<function_name>" that belongs to project with name "test_project_function_upd_without_values" using this "<data_upd>" as new data
    Then I expect an error as result
    And I expect to have 400 as code from response
    And I expect to have this alert "<alert>" for "<field>" field
    Examples:
      | update_method | function_name                                    | field            | alert                                                         | data                                                                                                                                   | data_upd                                                                                                                          |
      | PUT           | test_function_put_upd_without_name               | name             | This field may not be blank                                   | {"name":"test_function_put_upd_without_name","sql": "SELECT * from test_project_function_upd_without_values.test_table"}               | {"name":"","sql": "SELECT * from test_project_function_upd_without_values.test_table"}                                            |
      | PATCH         | test_function_patch_upd_without_name             | name             | This field may not be blank                                   | {"name":"test_function_patch_upd_without_name","sql": "SELECT * from test_project_function_upd_without_values.test_table"}             | {"name":"","sql": "SELECT * from test_project_function_upd_without_values.test_table"}                                            |
      | PUT           | test_function_put_upd_without_sql                | sql              | This field may not be blank                                   | {"name":"test_function_put_upd_without_sql","sql": "SELECT * from test_project_function_upd_without_values.test_table"}                | {"name":"test_function_put_upd_without_sql","sql": ""}                                                                            |
      | PATCH         | test_function_patch_upd_without_sql              | sql              | This field may not be blank                                   | {"name":"test_function_patch_upd_without_sql","sql": "SELECT * from test_project_function_upd_without_values.test_table"}              | {"name":"test_function_patch_upd_without_sql","sql": ""}                                                                          |
      | PUT           | test_function_put_upd_with_object_inside         | non_field_errors | Invalid data. Expected a dictionary, but got list             | {"name":"test_function_put_upd_with_object_inside","sql": "SELECT * from test_project_function_upd_without_values.test_table"}         | [{"name":"test_function","sql":"SELECT * FROM test_project_function_upd_without_values.test_table_venom_functions FORMAT JSON"}]  |
      | PATCH         | test_function_patch_upd_with_object_inside       | non_field_errors | Invalid data. Expected a dictionary, but got list             | {"name":"test_function_patch_upd_with_object_inside","sql": "SELECT * from test_project_function_upd_without_values.test_table"}       | [{"name":"test_function","sql":"SELECT * FROM test_project_function_upd_without_values.test_table_venom_functions FORMAT JSON"}]  |
      | PUT           | test_function_put_upd_with_distinct_characters   | name             | Name can only contain alphanumeric characters and underscores | {"name":"test_function_put_upd_with_distinct_characters","sql": "SELECT * from test_project_function_upd_without_values.test_table"}   | {"name":"new_name'-*/?@#$","sql":"SELECT * FROM test_project_function_upd_without_values.test_table_venom_functions FORMAT JSON"} |
      | PATCH         | test_function_patch_upd_with_distinct_characters | name             | Name can only contain alphanumeric characters and underscores | {"name":"test_function_patch_upd_with_distinct_characters","sql": "SELECT * from test_project_function_upd_without_values.test_table"} | {"name":"new_name'-*/?@#$","sql":"SELECT * FROM test_project_function_upd_without_values.test_table_venom_functions FORMAT JSON"} |

  @api @functions @regression @delete_shared_resource
  Scenario Outline: Update function inside a non existing organization [404]
    Given I create a project with name "test_project_function_upd_wrong_org" just one time
    Then I expect a created successfully as result
    When I create a function with name "<function_name>" and sql "SELECT * FROM test_project_function_upd_wrong_org.test_function_venom_functions FORMAT JSON" for project "test_project_function_upd_wrong_org" just one time
    Then I expect a created successfully as result
    Given I try to work with a non existing organization
    When Via <update_method> I change the function with name "<function_name>" that belongs to project with name "test_project_function_upd_wrong_org" using as name "new_name" as new data
    Then I expect an error as result
    And I expect to have 404 as code from response
    And I expect to have this alert "Not found" for "detail" field
    Examples:
      | update_method | function_name                    |
      | PUT           | test_function_put_upd_fake_org   |
      | PATCH         | test_function_patch_upd_fake_org |

  @api @functions @regression
  Scenario Outline: Update function by using an invalid project [404]
    When Via <update_method> I change the function with id "<function_id>" that belongs to project with id "<project_id>" using as name "new_name" as new data
    Then I expect an error as result
    And I expect to have 404 as code from response
    And I expect to have this alert "Not found" for "detail" field
    Examples:
      | update_method | function_id                        | project_id |
      | PUT           | test_function_put_upd_fake_proj    | 123        |
      | PATCH         | test_function_patch_upd_fake_proj  | 123        |
      | PUT           | test_function_put_upd_empty_proj   |            |
      | PATCH         | test_function_patch_upd_empty_proj |            |

  @api @functions @regression @delete_shared_resource
  Scenario Outline: Update function using an invalid function [404]
    Given I create a project with name "test_project_function_upd_wrong_function" just one time
    Then I expect a created successfully as result
    When Via <update_method> I change the function with id "<function_id>" that belongs to project with name "test_project_function_upd_wrong_function" using as name "new_name" as new data
    Then I expect an error as result
    And I expect to have 404 as code from response
    And I expect to have this alert "Not found" for "detail" field
    Examples:
      | update_method | function_id   |
      | PUT           | fake_function |
      | PATCH         | fake_function |

  @api @functions @regression
  Scenario: Delete function using an invalid token [401]
    Given I create a project with name "project_function_delete_wrong_token"
    Then I expect a created successfully as result
#    When I create a function with name "function_delete_wrong_token"
    Given I am using a fake token
    When I delete the function with id "function_delete_wrong_token" for project with name "project_function_delete_wrong_token"
    Then I expect an error as result
    And I expect to have 401 as code from response
    And I expect to have an error message about invalid token

  @api @functions @regression @sanity @smoke
  Scenario: Delete function without using a token [401]
    Given I create a project with name "project_function_delete_no_token"
    Then I expect a created successfully as result
#    When I create a function with name "function_delete_no_token"
#    Then I expect a created successfully as result
    Given I am not authenticated
    When I delete the function with id "function_delete_no_token" for project with name "project_function_delete_no_token"
    Then I expect an error as result
    And I expect to have 401 as code from response
    And I expect to have an error message about invalid credentials

  @api @functions @regression
  Scenario Outline: Delete function by using an invalid project [404]
    When I delete the function with id "test123" for project with id "<project_id>"
    Then I expect an error as result
    And I expect to have 404 as code from response
    And I expect to have this alert "Not found" for "detail" field
    Examples:
      | project_id |
      | 123        |
      | fakeId     |
      |            |

  @api @functions @regression
  Scenario: Delete function inside a non existing organization [404]
    Given I create a project with name "project_function_delete_wrong_org"
    Then I expect a created successfully as result
    When I create a function with name "function_delete_wrong_org" for project "project_function_delete_wrong_org"
    Then I expect a created successfully as result
    Given I try to work with a non existing organization
    When I delete the function with name "function_delete_wrong_org" for project with name "project_function_delete_wrong_org"
    Then I expect an error as result
    And I expect to have 404 as code from response
    And I expect to have this alert "Not found" for "detail" field

  @api @functions @regression
  Scenario Outline: Delete function by using an invalid function [404]
#    Given I create a project with name "project_function_delete_wrong_function" just one time
#    Then I expect a created successfully as result
    When I delete the function with id "<function_id>" for project with id "project_function_delete_wrong_function"
    Then I expect an error as result
    And I expect to have 404 as code from response
    And I expect to have this alert "Not found." for "detail" field
    Examples:
    | function_id |
    | 123        |
    | fakeId     |

  @api @functions @regression @sanity @smoke @apiOperation:config_v1_orgs_projects_functions_destroy
  Scenario: Delete function [204]
    Given I create a project with name "project_function_delete"
    Then I expect a created successfully as result
    When I create a function with name "function_delete" for project "project_function_delete"
    Then I expect a created successfully as result
    When I delete the function with name "function_delete" for project with name "project_function_delete"
    Then I expect a deleted as result
