import streamlit as st
import bcrypt
from database import create_user, get_user_by_email, get_user_by_username
from utils import validate_email, validate_password, validate_username   


def hash_password(password: str) -> str:
     
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
     
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def show_auth_page():
     

    st.set_page_config(page_title="Python Chatbot — Login", page_icon="🔐")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("## 🧑‍🏫 Python Virtual Teacher")
        st.markdown("---")

        tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])

        
        with tab1:
            st.subheader("Welcome Back!")

            email = st.text_input(
                "Email",
                placeholder="you@example.com",
                key="login_email"
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                key="login_password"
            )

            if st.button("Login 🚀", use_container_width=True, type="primary"):
                if not email or not password:
                    st.error("Please fill in all fields!")

                elif not validate_email(email):                 
                    st.error("Invalid email format!")

                else:
                    user = get_user_by_email(email)
                    if user and verify_password(password, user["password"]):
                        st.session_state.logged_in = True
                        st.session_state.username = user["username"]
                        st.session_state.email = email
                        st.success(f"Welcome back, {user['username']}! 🎉")
                        st.rerun()
                    else:
                        st.error("❌ Invalid email or password!")

        
        with tab2:
            st.subheader("Create Account")

            new_username = st.text_input(
                "Username",
                placeholder="raghav123",
                key="reg_username"
            )
            new_email = st.text_input(
                "Email",
                placeholder="you@example.com",
                key="reg_email"
            )
            new_password = st.text_input(
                "Password",
                type="password",
                placeholder="Min 6 chars, 1 uppercase, 1 number",
                key="reg_password"
            )
            confirm_password = st.text_input(
                "Confirm Password",
                type="password",
                placeholder="Repeat password",
                key="reg_confirm"
            )

            if st.button("Create Account ✨", use_container_width=True, type="primary"):

                 
                if not all([new_username, new_email, new_password, confirm_password]):
                    st.error("Please fill in all fields!")

                 
                else:
                    is_valid, msg = validate_username(new_username)
                    if not is_valid:
                        st.error(msg)

                     
                    elif not validate_email(new_email):
                        st.error("Invalid email format!")

                     
                    else:
                        is_valid, msg = validate_password(new_password)
                        if not is_valid:
                            st.error(msg)

                         
                        elif new_password != confirm_password:
                            st.error("Passwords do not match!")

                         
                        elif get_user_by_username(new_username):
                            st.error("Username already taken!")

                       
                        else:
                            hashed = hash_password(new_password)
                            success = create_user(new_username, new_email, hashed)
                            if success:
                                st.success("✅ Account created! Please login now.")
                            else:
                                st.error("Email already registered!")