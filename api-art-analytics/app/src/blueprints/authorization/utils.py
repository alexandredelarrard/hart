def confirmation_email_html(new_user, confirm_url):
    confirm_url = confirm_url.replace("localhost", "localhost:3000")
    intro = f"<p>Bonjour {new_user.surname},</p>"
    button = f"""
    <p>Cliquez sur le bouton suivant afin de confirmer votre email:</p>
    <a href="{confirm_url}" style="text-decoration: none;">
        <button style="
            background-color: #154d89;
            border: none;
            color: white;
            padding: 15px 32px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 12px;
        ">Confirmer votre email</button>
    </a>
    """
    signature = f"""
    <p>l'équipe Artyx</p>
    <img src="https://localhost:3000/logo.png" alt="Artyx Logo" style="width:150px;height:auto;">
    """
    return intro + button + signature


def reset_email_html(new_user, confirm_url):
    confirm_url = confirm_url.replace("localhost", "localhost:3000")
    intro = f"<p>Bonjour {new_user.surname},</p>"
    button = f"""
    <p>Voici le bouton pour réinitialiser votre mot de passe:</p>
    <a href="{confirm_url}" style="text-decoration: none;">
        <button style="
            background-color: #154d89;
            border: none;
            color: white;
            padding: 15px 32px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 12px;
        ">Réinitialiser votre mot de passe</button>
    </a>
    """
    signature = f"""
    <p>l'équipe Artyx</p>
    <img src="https://localhost:3000/logo.png" alt="Artyx Logo" style="width:150px;height:auto;">
    """
    return intro + button + signature
