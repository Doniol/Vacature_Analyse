from dataset_converter import create_dataset
from pipelines.pipeline_testdatabase import pipeline_converter_to_testsetdb


def main():
    # Enter database details
    host="weert.lucimmerzeel.nl"
    port="5432"
    database="pocdb"
    user="pocuser"
    password="pocuser"
    
    # Create connection to database
    pipe = pipeline_converter_to_testsetdb(host, port, database, user, password)

    # Create dataset
    dataset = create_dataset("dataset\\vacature_testset_txtformat.txt")
    # Save dataset to database
    pipe.push_to_database(dataset)

    # Get dataset from database
    print(pipe.pull_from_database())


main()