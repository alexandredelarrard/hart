import React from 'react';
import HeaderWhite from "./Header_white.js";
import { COMPANY_NAME } from "../../utils/constants.js";
import { Link } from 'react-router-dom';
import '../../css/Terms.css';

const Terms = ({t}) => {
  return (
    <div>
      <HeaderWhite t={t}/>
        <div className="terms-container">
            <h1>{t("landing_page.terms.supertitle")}</h1>

            <h2>{t("landing_page.terms.title1")}</h2>
            <p>{t("landing_page.terms.desc1")}</p>

            <h2>{t("landing_page.terms.title2")}</h2>
            <p>{t("landing_page.terms.desc2").replace('{COMPANY_NAME}', COMPANY_NAME)}</p>

            <h2>{t("landing_page.terms.title3")}</h2>
            <p>{t("landing_page.terms.desc3")}</p>

            <h3>{t("landing_page.terms.title4")}</h3>
                <p>
                {t("landing_page.terms.desc4")}
                <ul>
                    <li>{t("landing_page.terms.item1")}</li>
                    <li>{t("landing_page.terms.item2")}</li>
                    <li>{t("landing_page.terms.item3")}</li>
                </ul>
            </p>

            <h3>{t("landing_page.terms.title5")}</h3>
            <p>
                {t("landing_page.terms.desc5")}
                <ul>
                    <li>{t("landing_page.terms.item4")}</li>
                    <li>{t("landing_page.terms.item5")}</li>
                    <li>{t("landing_page.terms.item6")}</li>
                    <li>{t("landing_page.terms.item7")}</li>
                </ul>
            </p>

            <h3>{t("landing_page.terms.title6")}</h3>
            <p>
                {t("landing_page.terms.desc6")}
                <ul>
                    <li>{t("landing_page.terms.item8")}</li>
                    <li>{t("landing_page.terms.item9")}</li>
                    <li>{t("landing_page.terms.item10")}</li>
                    <li>{t("landing_page.terms.item11")}</li>
                    <li>{t("landing_page.terms.item12")}</li>
                    <li>{t("landing_page.terms.item13")}</li>
                </ul>
                {t("landing_page.terms.desc6sup")} <Link to="/contact">{t("landing_page.terms.contact")}</Link>.
            </p>

            <h2>{t("landing_page.terms.title7")}</h2>
            <p>{t("landing_page.terms.desc7")}</p>

            <h2>{t("landing_page.terms.title8")}</h2>
            <p>{t("landing_page.terms.desc8").replace("{COMPANY_NAME}", COMPANY_NAME)} <Link to="/contact">{t("landing_page.terms.contact")}</Link>.</p>

            <h2>{t("landing_page.terms.title9")}</h2>
            <p>{t("landing_page.terms.desc9").replace("{COMPANY_NAME}", COMPANY_NAME)}</p>

            <h2>{t("landing_page.terms.title10")}</h2>
            <p>{t("landing_page.terms.desc10")}</p>

            <h2>{t("landing_page.terms.title11")}</h2>
            <p>{t("landing_page.terms.desc11")} <Link to="/contact">{t("landing_page.terms.contact")}</Link>.</p>

        </div>
    </div>
  );
};

export default Terms;