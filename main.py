# import mysql.connector
#
# # Connect to the database
# cnx = mysql.connector.connect(user='your_username', password='your_password',
#                               host='your_host',
#                               database='your_database')
#
# # Define the query to delete records that meet specific condition
# query = ("DELETE FROM your_table WHERE some_column = 'some_value'")
#
# # Execute the query
# cursor = cnx.cursor()
# cursor.execute(query)
# cnx.commit()
#
# # Close the cursor and connection
# cursor.close()
# cnx.close()
