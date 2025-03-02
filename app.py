from flask import Flask, render_template, request, session, redirect, url_for
import ollama

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required for session storage

def format_response(response_text):
    """
    Converts a response into a proper bullet-point format if the user requested it.
    """
    lines = response_text.split("\n")  # Split into lines
    formatted_lines = []

    for line in lines:
        line = line.strip()
        if line and not line.startswith("- ") and not line[0].isdigit():  
            formatted_lines.append(f"• {line}")  # Add bullet points
        else:
            formatted_lines.append(line)

    return "\n".join(formatted_lines)  # Join the lines back


@app.route("/", methods=["GET", "POST"])
def chat():
    if "history" not in session:
        session["history"] = []  # Initialize chat history

    if request.method == "POST":
        user_input = request.form["message"]

        # Check if the user asked for an answer in points
        if "in points" in user_input.lower() or "list" in user_input.lower():
            prompt = user_input + "\n\nPlease provide the answer in a structured bullet-point format."
        else:
            prompt = user_input

        response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
        reply = response['message']['content']
        formatted_reply = format_response(reply)  # Format the reply properly

        # Store messages in session
        session["history"].append({"role": "user", "content": user_input})
        session["history"].append({"role": "bot", "content": formatted_reply})
        session.modified = True  # Save session updates

    return render_template("index.html", chat_history=session["history"])


@app.route("/clear", methods=["POST"])
def clear_chat():
    session.pop("history", None)  # Remove chat history
    return redirect(url_for("chat"))  # Redirect to homepage


if __name__ == "__main__":
    app.run(debug=True)
