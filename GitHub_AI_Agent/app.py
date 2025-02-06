from flask import Flask, request, render_template
import pandas as pd
from user_interface.uploader import load_data, save_data
from data_cleaning.cleaning_agent import AIDataCleaningAgent

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files["file"]
        df = pd.read_csv(file)

        cleaning_agent = AIDataCleaningAgent(df)
        cleaned_df = cleaning_agent.clean_data()
        cleaned_df.to_csv("cleaned_data/web_cleaned_data.csv", index=False)

        return "✅ Data cleaned successfully! Download cleaned_data/web_cleaned_data.csv"

    return '''
        <form method="post" enctype="multipart/form-data">
            Upload your dataset: <input type="file" name="file">
            <input type="submit" value="Upload & Clean">
        </form>
    '''

if __name__ == "__main__":
    app.run(debug=True)
