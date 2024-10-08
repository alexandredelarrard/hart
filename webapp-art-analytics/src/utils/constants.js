export const URL_API='http://localhost:80'; //middle api nginx
export const URL_API_BACK='http://127.0.0.1:2000'; //backend nginx
export const ROOT_PICTURE='http://localhost:4000'; // picture s3
export const CARDS_PER_PAGE=36;
export const COMPANY_NAME='Arlitycs';

// AXIOS path to back apis
export const URL_LOGIN='/login';
export const URL_CHECK_LOGIN = "/protected";
export const URL_LOGOUT = "/logout";
export const URL_REFRESH_LOGIN="/refresh";
export const URL_SIGNIN='/signin';
export const URL_UPLOAD='/process';
export const URL_GET_TASK='/task_status';
export const URL_GET_IDS_INFO='/ids_infos';
export const URL_RESET_PASSWORD="/reset-password";
export const URL_GET_TASK_RESULTS="/get-past-results"
export const URL_SET_NEW_PASSWORD="/set-new-password";
export const URL_DELETE_TASK_RESULT="/delete-task";
export const LOG_ACTIVITY="/log-activity";
export const URL_GET_PAYMENTS="/user-payment-infos";
export const URL_UPDATE_PROFILE="/update-user-profile";
export const URL_GET_EXPERTS='/get-experts-close';
export const URL_SEARCH_DB='/search-items';
export const URL_GET_CHATBOT='/chatbot';
export const URL_ADD_TO_NEWSLETTER = "/add-newsletter";
export const URL_MY_ACTIVITY = "/user-my-activity-settings";
export const URL_CONTACT_US = "/contact-us"

// website href path internal to react
export const PATHS = {
    "LOGIN": "/login",
    "HOME": "/",
    "HOME_PRICING": "/#pricing",
    "HOME_PRODUCT": "/#product",
    "ANALYTICS": "/analytics",
    "TRIAL": "/trial",
    "CONTACT": "/contact",
    "ABOUT": "/about",
    "SOON": "/coming-soon",
    "TERMS": "/terms",
    "CGV": "/cgv",
    "BLOG": "/blog",
    "ENROLL": "/enroll",
    "RESET_PWD": "/reset-password",
    "CONFIRM_PWD": "/confirm/:token",
    "SET_NEW_PWD": "/set-new-password/:token",
    "CARD_ID": "/analytics/card/:id",
    "CARD_ID_ROOT": "/analytics/card/"
}
