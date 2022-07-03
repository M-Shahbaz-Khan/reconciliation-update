data = [
        {
                'sheet_name' : 'Airtable_Chubb_Statement',
                'airtable_name' : 'Chubb Statement of Account',
                'base' : 'appX4eY4wipGvD2n4',
                'filter_pol_number' : 'PrimaryPolicyNum',
                'filter_control_number' : 'PrimaryPolicyNum'
        },
        {
                'sheet_name' : 'Airtable_WC_Policies',
                'airtable_name' : 'Policies',
                'base' : 'app9RJbzpT3jQFn1A',
                'copy' : {'fields.Legal Name' : 'fields.DBA Name'}
        },
        {
                'sheet_name' : 'Airtable_Stripe_Customers',
                'airtable_name' : 'Stripe Customers',
                'base' : 'appwOl9KTOCPqh7ax',
        },
        {
                'sheet_name' : 'Airtable_Premium_Audit',
                'airtable_name' : 'Premium Audit',
                'base' : 'appHj9Yo9OoPWpgLQ',
                'filter_pol_number' : 'Policy Number Text [DND]',
                'rename' : {'fields.Id':'fields.id'}
        },
        {
                'sheet_name' : 'WCS_Transaction_History',
                'airtable_name' : 'WCS Transaction History',
                'base' : 'appjFfjDxAogLiXWI',
                'filter_pol_number' : 'policy_number_text',
        },
        {
                'sheet_name' : 'WCS_General',
                'airtable_name' : 'WCS General',
                'base' : 'appjFfjDxAogLiXWI',
                'filter_pol_number' : 'policy_number_text',
        },
        {
                'sheet_name' : 'WCS_Contracts',
                'airtable_name' : 'WCS Contracts',
                'base' : 'appjFfjDxAogLiXWI',
                'filter_pol_number' : 'policy_number_text',
        },
        {
                'sheet_name' : 'WCS_All_Links',
                'airtable_name' : 'WCS All Links',
                'base' : 'appjFfjDxAogLiXWI',
                'filter_pol_number' : 'policy_number_text',
        },
        {
                'sheet_name' : 'WCS_Exposures',
                'airtable_name' : 'WCS Exposures',
                'base' : 'appjFfjDxAogLiXWI',
                'filter_pol_number' : 'policy_number_text',
        },
        {
                'sheet_name' : 'WCS_State_Rating',
                'airtable_name' : 'WCS State Rating',
                'base' : 'appjFfjDxAogLiXWI',
                'filter_pol_number' : 'policy_number_text',
        },
        {
                'sheet_name' : 'Airtable_Chubb_AP',
                'airtable_name' : '[WC] Chubb AP',
                'base' : 'app9RJbzpT3jQFn1A',
                'filter_pol_number' : 'Policy Numbers (from WC Policies)',
        },
        {
                'sheet_name' : 'Airtable_Chubb_RP',
                'airtable_name' : '[WC] Chubb RP',
                'base' : 'app9RJbzpT3jQFn1A',
                'filter_pol_number' : 'Policy Number',
        },
        {
                'sheet_name' : 'Airtable_Stripe_Payments',
                'airtable_name' : 'Stripe Payments',
                'base' : 'app9RJbzpT3jQFn1A',
                'filter_bureau_id' : 'Risk Group Id (metadata) (from Customer ID)',
        },
        {
                'sheet_name' : 'Airtable_Stripe_Invoices',
                'airtable_name' : 'Stripe Invoices',
                'base' : 'app9RJbzpT3jQFn1A',
                'filter_bureau_id' : 'Risk Group Id (metadata) (from Customer)',
        },
        {
                'sheet_name' : 'Airtable_Glow_Payments',
                'airtable_name' : 'Glow Payments',
                'base' : 'appzMh02XqmJGbjlo',
                'rename' : {'fields._does Premium Match Paid Amount' : 'fields._does Premium Match Stripe Paid Amount'},
                'filter_pol_number' : 'Policy Numbers (from WC Policies)'
        },
]