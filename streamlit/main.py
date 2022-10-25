from email.policy import default
import streamlit as st
import warnings
warnings.filterwarnings('ignore')
import pandas as pd
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode
from connection import *
from queries import *
from streamlit_option_menu import option_menu
from data import amenities
from millify import millify


st.subheader(' Rental Properties Search ')

features_list = {}
with st.sidebar:

    selected = option_menu(
            menu_title = 'Main menu',
            options = ['Rental Properties Search',"Visualizations-Use Cases",'Model Training and Predictions'],
            orientation = "vertical",
            icons=['building','clipboard-data']


        )


if selected == 'Rental Properties Search':
    price_prediction_selected = option_menu(
            menu_title = 'Rental Properties Search',
            options = ['Features'],
            orientation = "horizontal",
            menu_icon='house',
            icons=['building','minecart','file-text']


        )

    if price_prediction_selected=='Features':
    
    
        #Enter number of bedrooms
        max_value_of_beds ,min_value_of_beds = get_range_of_values('BEDS')
        bed_count =['Studio']
        for bed in range(int(min_value_of_beds)+1,int(max_value_of_beds)+1):
            bed_count.append(bed)
        beds = st.selectbox(label = "Number of bedrooms", options= [1,2,3,4,5,6,7,8],
        index=2, key=None,
        disabled=False)
        features_list['beds']=beds

        #Enter number of bathrooms
        max_value_of_baths ,min_value_of_baths = get_range_of_values('BATHS')
        bath_count =[0.5]
        baths = st.selectbox(label = 'Number of bathrooms', options=[0.5,1,1.5,2,2.5,3,3.5],
        index =1, key=None,
        disabled=False)
        features_list['baths'] = baths

        max_sqfeet ,min_sqfeet = get_range_of_values('SQFEET')
        sqfeet = st.slider('Enter the amount of area needed (in sqfeet) ', int(min_sqfeet), int(max_sqfeet),value=1500)
        features_list['sqfeet'] = sqfeet



        st.subheader('Pets')

        if st.checkbox(label="Dogs"):
            features_list['dogs'] = 1
        else:
            features_list['dogs'] = 0

        if st.checkbox(label="Cats"):
            features_list['cats'] = 1
        else:
            features_list['cats'] = 0

       
       
   

        st.subheader('Amenities list')

        amenities_copy = amenities
        for i in amenities_copy:
            if i not in features_list:
                features_list[i] = 0

        amenities_list = st.multiselect(label = 'Select amenities',options=[amenity for amenity in amenities])

        for i in range(len(amenities_list)):
            features_list[amenities_list[i]] = 1
        
        st.session_state['features_list'] =features_list


        #Getting the matching records from the test dataset 
        if st.button(label='Find apartments'):
            records = get_matching_records(features_list)
            st.session_state['predictions'] = records
            st.write(st.session_state.predictions)
        

if selected=='Visualizations-Use Cases':
    if 'predictions' not in st.session_state:
        st.write("Please enter the records first")

    else:
        predictions = st.session_state['predictions']
        #Example controlers
        st.sidebar.subheader("St-AgGrid example options")

        sample_size = st.sidebar.number_input("rows", min_value=10, value=30)
        grid_height = st.sidebar.number_input("Grid height", min_value=200, max_value=800, value=300)

        return_mode = st.sidebar.selectbox("Return Mode", list(DataReturnMode.__members__), index=1)
        return_mode_value = DataReturnMode.__members__[return_mode]

        update_mode = st.sidebar.selectbox("Update Mode", list(GridUpdateMode.__members__), index=6)
        update_mode_value = GridUpdateMode.__members__[update_mode]


        #Enterprise modules

        enable_enterprise_modules = st.sidebar.checkbox("Enable Enterprise Modules")
        if enable_enterprise_modules:
            enable_sidebar =st.sidebar.checkbox("Enable grid sidebar", value=False)
        else:
            enable_sidebar = False

        #features

        enable_selection=st.sidebar.checkbox("Enable row selection", value=True)
        if enable_selection:
            st.sidebar.subheader("Selection options")
            selection_mode = st.sidebar.radio("Selection Mode", ['single','multiple'], index=1)

            use_checkbox = st.sidebar.checkbox("Use check box for selection", value=True)
            if use_checkbox:
                groupSelectsChildren = st.sidebar.checkbox("Group checkbox select children", value=True)
                groupSelectsFiltered = st.sidebar.checkbox("Group checkbox includes filtered", value=True)

            if ((selection_mode == 'multiple') & (not use_checkbox)):
                rowMultiSelectWithClick = st.sidebar.checkbox("Multiselect with click (instead of holding CTRL)", value=False)
                if not rowMultiSelectWithClick:
                    suppressRowDeselection = st.sidebar.checkbox("Suppress deselection (while holding CTRL)", value=False)
                else:
                    suppressRowDeselection=False
            st.sidebar.text("___")

    
        #Infer basic colDefs from dataframe types
        gb = GridOptionsBuilder.from_dataframe(st.session_state.predictions)
        gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum', editable=True)


        if enable_sidebar:
            gb.configure_side_bar()

        if enable_selection:
            gb.configure_selection(selection_mode)
            if use_checkbox:
                gb.configure_selection(selection_mode, use_checkbox=True, groupSelectsChildren=groupSelectsChildren, groupSelectsFiltered=groupSelectsFiltered)
            if ((selection_mode == 'multiple') & (not use_checkbox)):
                gb.configure_selection(selection_mode, use_checkbox=False, rowMultiSelectWithClick=rowMultiSelectWithClick, suppressRowDeselection=suppressRowDeselection)

        gb.configure_grid_options(domLayout='normal')
        gridOptions = gb.build()

        #Display the grid
        st.header("Visualizing the data points")
        st.markdown("""
            The user is able to filter columns according to a certain value, sort them from increasing order
            or decreasing order as needed. 
            Using the options given on the left side , a user can select rows which he wants to visualize.
        """)

        st.subheader('House records formatted in a table')

        grid_response = AgGrid(
            predictions, 
            gridOptions=gridOptions,
            height=grid_height, 
            width='100%',
            data_return_mode=return_mode_value, 
            update_mode=update_mode_value,
            enable_enterprise_modules=enable_enterprise_modules,
            )

        df = grid_response['data']
        selected = grid_response['selected_rows']
        selected_df = pd.DataFrame(selected)
        if selected:
            # st.subheader('Plotting and visualizing the data points corresponding to houses')
            # st.map(selected_df)
                          

            #Use Case 1 : 

            use_cases = st.selectbox(label = '',options = ['Get Summary information for nearby rentals','Search discounted houses around the area','Ranking properties according to their national park area and park count','Select an option'],index = 3)
            if use_cases == 'Get Summary information for nearby rentals':
                buffer_miles = st.text_input(label='Enter number of miles that you want to create a buffer:',value=0)
                if buffer_miles!='0':
                    with st.spinner(f'Generating summary information for nearby rentals within {buffer_miles} miles.. '):

                            
                            summary_list,properties_list = get_houses_in_the_area(selected_df['ID'][0],buffer_miles)
                            
                            st.subheader("Properties within the region:")
                            st.write(properties_list)
                            st.subheader('Statistics:') 
                            if summary_list[0] != None or summary_list[1] !=None or summary_list[2] != None:
                                st.write(f"Maximum price : {summary_list[0]}$")
                                st.write(f"Minimum price : {summary_list[1]}$")
                                st.write(f"Average price : {millify(summary_list[2])}$")
                            else:
                                st.write('Summary information could not be found..')

            # Use case 2:
            #!--------------------------
            elif use_cases == 'Search discounted houses around the area':
                with st.spinner('Searching discounted houses around the area...'):
                    st.subheader('Discounted houses around the area:')
                    discounted_houses = get_discounted_houses(selected_df['ID'][0])
                    st.write(discounted_houses)

            #Use case 3:      
            elif use_cases == 'Ranking properties according to their national park area and park count':
                with st.spinner('Ranking properties in the region according to their total green area and park count ...'):
                    green_information = get_green_area(selected_df['ID'][0])
                    
                    if green_information[0]==200:
                        st.caption("Ranking properties in the region according to their total green area and park count:")
                        st.write(green_information[1])
                       
                    else:
                        st.write(green_information[1])




if selected=='Model Training and Predictions':
    import subprocess

    st.subheader('Training the model')
    st.write('''You no longer have to go in the command line and type in the commands in order to train a model. 
    With the click of a single button , you have the power to train the model yourself.''')
    if st.button('Train the model'):

        with st.spinner('Training your model...'):
            subprocess.run('python model.py',shell=True)
            all_records = get_all_records()
            st.write('Model has been successfully trained')
        st.write('Predictions:')    
        st.write(all_records)