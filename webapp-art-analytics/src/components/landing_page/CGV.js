import React from 'react';
import Header from "./Header.js";
import { COMPANY_NAME } from "../../utils/constants.js";
import { Link } from 'react-router-dom';
import '../../css/Terms.css';

const CGV = ({t}) => {

  return (
    <div>
      <Header scrolled={true} t={t}/>
      <div className="terms-container">
        <h1>{t("cgv.supertitle")}</h1>

        <h2>{t("cgv.title1").replace('{COMPANY_NAME}', COMPANY_NAME)}</h2>
        <p>
          {t("cgv.desc1")}
        </p>

        <h2>{t("cgv.title2")}</h2>
        <p>
          {t("cgv.desc2").replace('{COMPANY_NAME}', COMPANY_NAME)}
        </p>

        <h2>{t("cgv.title3")}</h2>
        <p>
          {t("cgv.desc3")}
        </p>

        <h2>{t("cgv.title4")}</h2>
        <p>
          {t("cgv.desc4")}
        </p>

        <h2>{t("cgv.title5")}</h2>
        <p>
          {t("cgv.desc5")}
        </p>

        <h2>{t("cgv.title6")}</h2>
        <p>
          {t("cgv.desc6")}
        </p>

        <h2>{t("cgv.title7")}</h2>
        <p>
          {t("cgv.desc7")}
        </p>

        <h2>{t("cgv.title8")}</h2>
        <p>
          {t("cgv.desc8").replace('{COMPANY_NAME}', COMPANY_NAME)}
        </p>

        <h2>{t("cgv.title9")}</h2>
        <p>
          {t("cgv.desc9")}
        </p>

        <h2>{t("cgv.title10")}</h2>
        <p>
          {t("cgv.desc10")} <Link to="/contact">{t("overall.contactus")}</Link>.
        </p>
      </div>
    </div>
  );
};

export default CGV;