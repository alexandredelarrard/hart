import React from 'react';
import Header from "./Header.js";
import { COMPANY_NAME } from "../../utils/constants.js";
import { Link } from 'react-router-dom';
import '../../css/Terms.css';

const CGV = ({t}) => {
  const replaceCompanyName = (text) => text.replace(/{COMPANY_NAME}/g, COMPANY_NAME);
  return (
    <div>
      <Header scrolled={true} t={t}/>
      <div className="terms-container">
        <h1>{t("landing_page.cgv.supertitle")}</h1>

        <h2>{t("landing_page.cgv.title1")}</h2>
        <p>
          {replaceCompanyName(t("landing_page.cgv.desc1"))}
        </p>

        <h2>{t("landing_page.cgv.title2")}</h2>
        <p>
          {replaceCompanyName(t("landing_page.cgv.desc2"))}
        </p>

        <h2>{t("landing_page.cgv.title3")}</h2>
        <p>
          {replaceCompanyName(t("landing_page.cgv.desc3"))}
        </p>

        <h2>{t("landing_page.cgv.title4")}</h2>
        <p>
          {replaceCompanyName(t("landing_page.cgv.desc4"))}
        </p>

        <h2>{t("landing_page.cgv.title5")}</h2>
        <p>
          {replaceCompanyName(t("landing_page.cgv.desc5"))}
        </p>

        <h2>{t("landing_page.cgv.title6")}</h2>
        <p>
          {t("landing_page.cgv.desc6")}
        </p>

        <h2>{t("landing_page.cgv.title7")}</h2>
        <p>
          {t("landing_page.cgv.desc7")}
        </p>

        <h2>{t("landing_page.cgv.title8")}</h2>
        <p>
          {replaceCompanyName(t("landing_page.cgv.desc8"))}
        </p>

        <h2>{t("landing_page.cgv.title9")}</h2>
        <p>
          {t("landing_page.cgv.desc9")}
        </p>

        <h2>{t("landing_page.cgv.title10")}</h2>
        <p>
          {t("landing_page.cgv.desc10")} <Link to="/contact">{t("overall.contactus")}</Link>.
        </p>
      </div>
    </div>
  );
};

export default CGV;